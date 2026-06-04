<%!
from alembic import op
import sqlalchemy as sa

try:
    _ = upgrades
except NameError:
    upgrades = None

try:
    _ = downgrades
except NameError:
    downgrades = None

try:
    _ = down_revision
except NameError:
    down_revision = None

try:
    _ = branch_labels
except NameError:
    branch_labels = None

try:
    _ = depends_on
except NameError:
    depends_on = None

%>

"""Auto-generated migration."""

revision = "${rev_id}"
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}

def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}
