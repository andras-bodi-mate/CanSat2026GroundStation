from pathlib import Path, PurePosixPath

class Core:
    projectDir = Path(__file__).resolve().parent.parent

    @staticmethod
    def getPath(path: str | Path):
        if isinstance(path, Path) and path.exists():
            return path
        else:
            return Core.projectDir / PurePosixPath(path)