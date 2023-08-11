import os
from typing import Any

from flask import Flask, jsonify, render_template_string, request, send_from_directory
from flask_cors import CORS

from database.database_worker import DatabaseWorder
from downloader.site_saver import SiteSaver, TelegraphProvider, TextProvider

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})
downloads_thread = []
worker = DatabaseWorder(os.path.join("server", "sites.db"))


@app.route("/site/<page_name>/<resource_name>", methods=["GET"])
def get_page_and_resources(page_name: str, resource_name: str) -> Any:
    if resource_name == "html":
        with open(
            os.path.join("server", "data", page_name, page_name + ".html")
        ) as file:
            return render_template_string(file.read())
    else:
        return send_from_directory(os.path.join("data", page_name), resource_name)


@app.route("/save", methods=["POST"])
def save_bunch() -> Any:
    post_data = request.get_json()
    type = post_data.get("crawler_type")
    text = post_data.get("text")
    match type:
        case "TelegraphProvider":
            url_provider = TelegraphProvider(TextProvider(text))
        case _:
            return jsonify("Unsupported provider")
    saver = SiteSaver(worker, url_provider)
    saver.start()
    downloads_thread.append(saver)
    return jsonify("Started download")


@app.route("/save/status", methods=["GET"])
def get_downloads_status() -> Any:
    global downloads_thread
    downloads_thread = [x for x in downloads_thread if x.is_alive()]
    return jsonify(
        [
            {
                "total_pages": x.get_total_pages_to_save(),
                "saved_pages": x.get_finished_downloads(),
            }
            for x in downloads_thread
        ]
    )


@app.route("/pages", methods=["POST"])
def get_pages() -> Any:
    post_data = request.get_json()
    page = post_data.get("page")
    pages_per_page = post_data.get("pages_per_page")
    return jsonify(
        worker.get_pages(page, pages_per_page if pages_per_page is not None else 5)
    )
