import click
import json
import hashlib
from pathlib import Path

from .editslist import EditsList


# hierarcharcl click usage:
# 1. create a group
# 2. add commands to the group
# 3. add the group to the main function
@click.group()
def project():
    pass


def is_project_dir(path: Path) -> bool:
    """Check if the given path is a project directory by looking for a .pyt folder"""
    return (path / ".pyt").exists() and (path / ".pyt").is_dir()


@project.command()
@click.argument("name")
def new(name):
    # lets create a new folder in the current directory
    path = Path.cwd() / name

    is_proj = is_project_dir(path)
    if path.exists():
        if is_proj:
            print(f"Project {name} already exists.")
        else:
            print(f"Directory {name} already exists.")
    else:
        print(f"Creating new project: {name}...")
        path.mkdir()
        (path / ".pyt").mkdir()


@project.command()
@click.argument("name", required=False)
def scan(name=None):
    """If the current directory is a project directory, scan it for files and folders and create a .pyt/manifest.json file"""
    if name is not None:
        path = Path.cwd() / name
    else:
        path = Path.cwd()

    if is_project_dir(path):
        # create a manifest dict to write to file
        new_manifest_files = {}

        # this list will contain all the delta packs, which are the deltas used to reconstruct the files from the previous version
        # Each file is indexed by it's sha here, and it contains all the diffs from the previous version
        delta_packs = {}

        print("Scanning project directory...")
        files = [str(f.relative_to(path)) for f in path.glob("**/*") if f.is_file()]
        files.sort()

        new_files = {}
        for f in files:
            with open(path / f, "rb") as file:
                new_files[path] = hashlib.sha256(file.read()).hexdigest()

        # if the manifest file already exists, diff it and update the chaindiff
        manifest_path = path / ".pyt/manifest.json"
        changed_files = []
        if manifest_path.exists():
            with open(manifest_path, "r") as file:
                old_manifest_files = json.load(file)

            # diff all sha256s and sum the changed sha256s only to get the new chaindiff
            for p, sha in new_files.items():
                if p in old_manifest_files:
                    if sha != old_manifest_files[p]:
                        changed_files.append(p)
                else:
                    changed_files.append(p)

        # now that we have the changed files, we can diff them and create the delta packs
        for p in new_files:
            if p.is_file():
                with open(p, "rb") as file:
                    new_file = file.read()

                if p in old_manifest_files:
                    with open(p, "rb") as file:
                        old_file = file.read()

                    # calculate the levenshtein distance between the two files and save the transformations needed to get from the old file to the new file, rather than just the distance
                    # this is done to allow for the reconstruction of the file from the previous version
                    edits = leven_edits(old_file, new_file)
                    delta_packs[p] = edits
                else:
                    delta_packs[p] = leven_edits(b"", new_file)
            else:
                continue

        # now that we have the delta packs, we can write them to the sha256 files in the .pyt folder
        # These files will be indexable by manifests built at each version, and will allow for the reconstruction of the files from the previous version
        for p, edits in delta_packs.items():
            with open(path / ".pyt" / f"{new_files[p]}.json", "w") as file:
                json.dump(edits, file)

        # now lets write the new manifest file
        with open(manifest_path, "w") as file:
            json.dump(new_files, file)

        print("Done.")


def main():
    project()


if __name__ == "__main__":
    main()
