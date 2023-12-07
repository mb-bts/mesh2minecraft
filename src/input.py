class FileReader:
    """Base class for reading and parsing files"""

    def __init__(self, file_path):
        """
        Initializes FileReader

        Args:
        - file_path (str): path to file location
        """
        self.file_path = file_path
        self.file_contents = None
        self.vertices = []
        self.faces = []
        self.colors = []
    
    def read_file(self):
        """Opens file (or handles corresponding error) and initiates reading and parsing"""
        try:
            with open(self.file_path, "r") as f:
                self.file_contents = f.read()
                self.parse()
        except FileNotFoundError:
            print(f"Couldn't find file: {self.file_path}")
        except Exception as e:
            print(f"Error reading input file: {str(e)}")

    def parse(self):
        """
        File parsing must be implemented by subclass
        
        Raises:
        - NotImplementedError
        """
        raise NotImplementedError("This must be implemented by a subclass")

class ObjReader(FileReader):
    """File reading and parsing logic specific to OBJ files"""

    def parse(self):
        """Extracts vertices, faces, and colors from OBJ files"""
        lines = self.file_contents.split("\n")
        for line in lines:
            data = line.strip().split()
            if not data:
                continue
            elif data[0] == "v":
                self.vertices.append([float(data[i]) for i in range(1, 4)])
                if len(data) > 4: # if vertex colors included in obj file then read these too
                    self.colors.append([float(data[i]) for i in range(4, 7)])
            elif data[0] == "f":
                self.faces.append([int(data[i].split("/")[0]) - 1 for i in range(1, 4)])