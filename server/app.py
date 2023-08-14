import os
from typing import Any

from flask import Flask, jsonify, render_template_string, request, send_from_directory
from flask_cors import CORS

from database.database_worker import DatabaseWorder
from downloader.site_saver import SiteSaver, TelegraphProvider, TextProvider

# instantiate the app


# enable CORS


class InnerApp:
    def __init__(
        self,
        db_path: str = os.path.join("server", "sites.db"),
        data_path: str = os.path.join("server", "data"),
    ) -> None:
        self._downloads_thread = []
        self._db_path = db_path
        self._data_path = data_path
        self._worker = DatabaseWorder(self._db_path)
        self._app = Flask(__name__)
        CORS(self._app, resources={r"/*": {"origins": "*"}})
        self._app.config.from_object(__name__)

        @self._app.route("/site/<page_name>/<resource_name>", methods=["GET"])
        def get_page_and_resources(page_name: str, resource_name: str) -> Any:
            if resource_name == "html":
                with open(
                    os.path.join(self._data_path, page_name, page_name + ".html"),
                    encoding="UTF-8",
                ) as file:
                    return render_template_string(file.read())
            else:
                return send_from_directory(
                    os.path.join("../", self._data_path, page_name), resource_name
                )

        @self._app.route("/save", methods=["POST"])
        def save_bunch() -> Any:
            post_data = request.get_json()
            type = post_data.get("crawler_type")
            text = post_data.get("text")
            match type:
                case "TelegraphProvider":
                    url_provider = TelegraphProvider(TextProvider(text))
                case _:
                    return jsonify("Unsupported provider")
            saver = SiteSaver(
                self._worker, url_provider, download_folder=self._data_path
            )
            saver.start()
            self._downloads_thread.append(saver)
            return jsonify("Started download")

        @self._app.route("/save/status", methods=["GET"])
        def get_downloads_status() -> Any:
            self._downloads_thread = [x for x in self._downloads_thread if x.is_alive()]
            return jsonify(
                [
                    {
                        "total_pages": x.get_total_pages_to_save(),
                        "saved_pages": x.get_finished_downloads(),
                    }
                    for x in self._downloads_thread
                ]
            )

        @self._app.route("/pages", methods=["POST"])
        def get_pages() -> Any:
            post_data = request.get_json()
            page = post_data.get("page")
            pages_per_page = post_data.get("pages_per_page")
            return jsonify(
                self._worker.get_pages(
                    page, pages_per_page if pages_per_page is not None else 5
                )
            )

    def get_app(self) -> Flask:
        return self._app


def create_app() -> Flask:
    return InnerApp().get_app()
