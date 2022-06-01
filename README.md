# WCL Ad Remover

Removes the ads from the Warcraft Logs uploader. Currently, only Linux AppImages are supported.


#### Quickstart
Build and run the docker container with the following commands or by executing `run.sh`
```
docker build . -t wcladremover 
docker run -v "$(pwd)"/output:/output wcladremover:latest
```

Change ownership of the output file and make it executable
```
sudo chown $USER output/War* && chmod +x output/War*
```

and then move the final AppImage wherever you want.

#### TODO:
- [ ] Windows build
- [ ] Mac build