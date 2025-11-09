from pathlib import Path
import logging
import subprocess
import sys


class Input_Validator:
    """Base class for input validation."""

    def __init__(self, path):
        if isinstance(path, str):
            return path
        else:
            raise TypeError("Path need to be string type")


class TFC(Input_Validator):
    """A class for cleaning Terraform state files and directories."""

    def __init__(self, path: str):

        super().__init__(path)

        self.path = Path(path)
        self._validate_path()

        self._tf_files_paths_set = set()
        self._modified_tf_files_paths = list()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger()

    def _validate_path(self) -> None:
        """Validate that the provided path exists."""
        if not self.path.exists():
            raise FileNotFoundError("Provided path does not exists")

    def _add_modified_terraform_paths_to_set(self) -> set:
        """Seek for terraform state occurences under give path and add those to set"""
        for root, dirnames, filenames in self.path.walk():
            if ".terraform" in dirnames:
                self._tf_files_paths_set.add(str(root))

    def _add_suffixes_to_paths(self) -> None:
        """Add suffixes to paths existing in set and returns list of 2 object lists"""
        if self._tf_files_paths_set:
            for path in self._tf_files_paths_set:
                self._modified_tf_files_paths.append(
                    [f"{path}/.terraform", f"{path}/.terraform.lock.hcl"])

    def _remove_targets(self) -> None:
        """Deletes terraform folders and files"""
        for pair in self._modified_tf_files_paths:
            subprocess.run(["rm", "-rf", pair[0]])
            self.logger.info(f"Removed directory: {pair[0]}")
            subprocess.run(["rm", "-f", pair[1]])
            self.logger.info(f"Removed file: {pair[1]}")

    def perform_tfc(self):
        """Perform terraform clean"""
        self.logger.info(f"Starting Terraform cleanup in: {self.path}")

        self._add_modified_terraform_paths_to_set()
        self._add_suffixes_to_paths()

        if not self._tf_files_paths_set:
            self.logger.info("No cleanup targets found")
            return True

        self._remove_targets()


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "."

    tfc = TFC(path)
    tfc.perform_tfc()


if __name__ == "__main__":
    main()
