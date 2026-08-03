"""板块蓝图：列表 + 详情"""
from flask import Blueprint
from app.extensions import db
from app.errors import success, NotFoundError
from app.models.post import Board

board_bp = Blueprint("board", __name__)


@board_bp.route("/", methods=["GET"])
def index():
    return success(data={"module": "board", "status": "ok"}, message="board blueprint ok")


@board_bp.route("", methods=["GET"])
def list_boards():
    """T12: 板块列表"""
    boards = Board.query.filter_by(status=1).order_by(Board.sort_order.asc()).all()
    return success(data=[{
        "id": b.id, "slug": b.slug, "name": b.name,
        "description": b.description, "icon": b.icon,
        "post_count": b.post_count,
    } for b in boards])


@board_bp.route("/<int:board_id>", methods=["GET"])
def get_board(board_id):
    """板块详情"""
    board = Board.query.get(board_id)
    if not board or board.status != 1:
        raise NotFoundError("板块不存在")
    return success(data={
        "id": board.id, "slug": board.slug, "name": board.name,
        "description": board.description, "icon": board.icon,
        "post_count": board.post_count,
    })
