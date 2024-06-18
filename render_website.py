import json
from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape


def on_reload():
    env = Environment(
        loader=FileSystemLoader("."), autoescape=select_autoescape(["html", "xml"])
    )

    template = env.get_template("template.html")

    rendered_page = template.render(marks="", cars="")

    with open("index.html", "w", encoding="UTF-8") as f:
        f.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch("template.html", on_reload)
    server.serve(root=".", default_filename="index.html")


if __name__ == "__main__":
    main()
