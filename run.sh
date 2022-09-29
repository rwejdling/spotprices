
#!/bin/bash
INTERVAL="${INTERVAL:=10}"
while true; do
  echo "`date` - running script..."
  time python3 app.py
  echo "`date` - script completed..."
  sleep $INTERVAL
done