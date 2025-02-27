from flask import Flask, request, jsonify
from crawling_service.crawler import crawl_schedule

app = Flask(__name__)

@app.route("/schedule", methods=["GET"])
def get_schedule():
    url = request.args.get("url")
    
    # URL 검증
    if not url:
        return jsonify({"code": "400", "message": "URL이 제공되지 않았습니다.", "is_success": False}), 400
    if not url.startswith("https://everytime.kr/"):
        return jsonify({"code": "400", "message": "잘못된 URL 형식입니다.", "is_success": False}), 400

    result = crawl_schedule(url)
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
    