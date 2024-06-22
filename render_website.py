import json
import os
from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape


def on_reload():
    env = Environment(
        loader=FileSystemLoader("."), autoescape=select_autoescape(["html", "xml"])
    )

    main_template = env.get_template("template.html")
    page_template = env.get_template("page_template.html")
    brands_folder = "pages"

    with open("brands.json", "r", encoding="UTF-8") as f:
        brands = json.load(f)

    with open("cars.json", "r", encoding="UTF-8") as f:
        automobiles = json.load(f)

    cars_on_page = 20

    for index, brand in enumerate(brands, start=1):
        brand_folder = f"{brand['brand_name']}"
        page_filename = f"page{index}.html"
        page_output_path = os.path.join(brands_folder, brand_folder, page_filename)
        os.makedirs(f"{brands_folder}/{brand_folder}", exist_ok=True)
        for automobile in automobiles:
            rendered_car_page = page_template.render(
                brand=brand, automobiles=automobiles
            )

            with open(page_output_path, "w", encoding="UTF-8") as f:
                f.write(rendered_car_page)

    rendered_page = main_template.render(brands=brands)

    with open("index.html", "w", encoding="UTF-8") as f:
        f.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch("template.html", on_reload)
    server.serve(root=".", default_filename="index.html")


if __name__ == "__main__":
    main()
