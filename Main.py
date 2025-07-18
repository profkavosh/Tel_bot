- name: Install Railway CLI
  run: |
    curl -sSL -o railway https://github.com/railwayapp/cli/releases/latest/download/railway
    file railway
    chmod +x railway
    sudo mv railway /usr/local/bin/railway
- name: Deploy to Railway (with action)
  uses: railwayapp/railway-action@v1
  with:
    railwayToken: ${{ secrets.RAILWAY_TOKEN }}
