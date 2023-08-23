**COMP3888_TH16_01_P51 Network Visualisation - Capstone Project**

1. Check node -v
2. Check npm -v
3. Change directories to src/frontend by `cd src/frontend/`
4. npm init, press enter for all selections

{
  "name": "my-electron-app",
  "version": "1.0.0",
  "description": "Hello World!",
  "main": "main.js",
  "author": "Jane Doe",
  "license": "MIT"
}

6. Install Electron package into your app's devDependencies: `npm install --save-dev electron`

7. In scripts field of package.json add 
`"scripts": {
    "start": "electron ."
  }
`