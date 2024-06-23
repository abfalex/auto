import json
import os
import pprint
from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked


def format_price(value):
    return f"{value:,}".replace(",", " ")


def on_reload():
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.filters["format_price"] = format_price

    main_template = env.get_template("template.html")
    page_template = env.get_template("page_template.html")
    pages_folder = "pages"

    with open("brands.json", "r", encoding="UTF-8") as f:
        brands = json.load(f)

    cars_on_page = 20
    all_automobiles = {}

    for brand_number, brand in enumerate(brands, start=1):
        brand_folder_name = f"{brand['brand_name']}"
        brand_page_path = os.path.join(pages_folder, brand_folder_name)

        os.makedirs(brand_page_path, exist_ok=True)

        brands_folder = os.path.join("brands")
        brand_folder_path = os.path.join(brands_folder, brand_folder_name)
        for brand_file in os.listdir(brand_folder_path):
            with open(f"{brand_folder_path}/{brand_file}", "r", encoding="UTF-8") as f:
                automobiles = json.load(f)
                auto_on_page = automobiles[0:cars_on_page]

                if brand["brand_name"] not in all_automobiles:
                    all_automobiles[brand["brand_name"]] = []
                all_automobiles[brand["brand_name"]].extend(auto_on_page)

            page_chucks = list(chunked(automobiles, 20))
            for page_number, automobiles in enumerate(page_chucks, start=1):
                page_filename = f"page{page_number}.html"
                page_output_path = os.path.join(brand_page_path, page_filename)

                rendered_car_page = page_template.render(
                    brands=brands,
                    brand=brand,
                    automobiles=automobiles,
                    page_number=brand_number,
                )

                with open(page_output_path, "w", encoding="UTF-8") as f:
                    f.write(rendered_car_page)

    rendered_page = main_template.render(
        brands=brands,
        page_number=brand_number,
        automobiles=all_automobiles,
        total_pages=len(brands),
    )

    with open("index.html", "w", encoding="UTF-8") as f:
        f.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch("template.html", on_reload)
    server.watch("page_template.html", on_reload)
    server.watch("base_template.html", on_reload)
    server.serve(root=".", default_filename="index.html")


if __name__ == "__main__":
    main()
