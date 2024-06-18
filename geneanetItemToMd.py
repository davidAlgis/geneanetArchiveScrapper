import os


class GeneanetItemToMd:
    def __init__(self, last_name, first_name, path_to_md, file_path_to_template):

        self.last_name = last_name
        self.first_name = first_name
        self.filename = f"{last_name}{first_name}.md"
        self.filepath = os.path.join(path_to_md, self.filename)

        # check if output directory exists, and if not, create it
        if not os.path.isdir(path_to_md):
            os.makedirs(path_to_md)

        # check if file exists, and if not, create it and copy the template into it
        if not os.path.isfile(self.filepath):
            with open(file_path_to_template, "r") as template_file:
                template_content = template_file.read()

            with open(self.filepath, "w") as f:
                f.write(template_content.format(
                    last_name=last_name, first_name=first_name))
