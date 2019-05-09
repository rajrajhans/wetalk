#!/usr/bin/env python

import sys
sys.path.insert(0, '../..')

from app import app
from models import initialize
app.run()
initialize()