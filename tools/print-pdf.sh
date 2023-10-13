#!/bin/sh

for f in "$(pwd)"/Presentation/*.md;
do
  echo "$f"
  filename=$(basename -s .md "$f")
  echo "======[Printing $filename file...]======"
  docker run --rm -t --net=host -v "$(pwd)/generation_tmp:/slides" astefanutti/decktape reveal -s 2048x1536 "http://localhost:1948/$filename.md" "$filename.pdf" || true
  mv -f "generation_tmp/$filename.pdf" "Presentation/doc/$filename.pdf" || true
done

