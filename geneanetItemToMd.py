import os

# global variable for the path to the markdown files
pathToMd = "/path/to/markdown/files"
# global variable for the path to the template file
filePathToTemplate = "/path/to/template.md"


class GeneanetItemToMd:
    def __init__(self, last_name, first_name):
        self.last_name = last_name
        self.first_name = first_name
        self.filename = f"{last_name}{first_name}.md"
        self.filepath = os.path.join(pathToMd, self.filename)

        # check if file exists, and if not, create it and copy the template into it
        if not os.path.isfile(self.filepath):
            with open(filePathToTemplate, "r") as template_file:
                template_content = template_file.read()

            with open(self.filepath, "w") as f:
                f.write(template_content.format(
                    last_name=last_name, first_name=first_name))
