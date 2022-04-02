
#!/bin/sh
INTERVAL="${INTERVAL:=10}"
while true; do
  echo "`date` - running script..."
  time python3 app.py
  sleep $INTERVAL
done