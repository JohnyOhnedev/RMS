"""Views for the RMS application, grouped into focused modules.

    auth_views      - candidate login/signup/logout
    resume_views    - upload, ATS analysis, job-role prediction, resources
    company_views   - company signup/login/dashboard, admin review queue
    admin_views     - custom admin dashboard
"""

from .auth_views import *  # noqa: F401,F403
from .company_views import *  # noqa: F401,F403
from .resume_views import *  # noqa: F401,F403
