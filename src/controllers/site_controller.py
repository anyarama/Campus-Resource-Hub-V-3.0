"""Public landing pages."""
from flask import Blueprint, render_template, request

from src.data_access.resource_dal import ResourceDAL

site_bp = Blueprint('site', __name__)


@site_bp.route('/')
def home():
    keyword = request.args.get('q', '').strip()
    highlighted = ResourceDAL.get_featured_resources(limit=4)
    stats = ResourceDAL.get_resource_stats()
    return render_template(
        'index.html',
        keyword=keyword,
        highlighted=highlighted,
        stats=stats,
    )


@site_bp.route('/style-guide')
def style_guide():
    """Simple route used by designers while iterating on Bootstrap components."""
    samples = ResourceDAL.get_featured_resources(limit=6)
    return render_template('style_guide.html', sample_resources=samples)
