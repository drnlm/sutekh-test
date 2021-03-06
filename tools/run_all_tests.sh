#!/bin/bash
# Neil Muller <drnlmuller+sutekh@gmail.com>, 2008
# Arguably not copyrightable, since this is basically self-evident,
# but, if a license is needed, consider this to be in the public domain

if which nosetests > /dev/null; then
   # Use nosetests if available
   echo "Running tests using nosetests"
   (cd ../sutekh && nosetests sutekh/tests)
else
   echo "Unable to find nosetests. Not running the test suite"
fi
