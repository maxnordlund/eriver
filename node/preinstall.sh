#!/usr/bin/env bash

if [ ! -f public/style/iceland.woff ]; then
  curl -o public/style/iceland.woff -O http://themes.googleusercontent.com/static/fonts/iceland/v2/9IfvfpywPgvB2I8dssFjDgLUuEpTyoUstqEm5AMlJo4.woff
  echo ":: Fetched font 'iceland.woff' from google"
fi
