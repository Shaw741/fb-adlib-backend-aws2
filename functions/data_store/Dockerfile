FROM public.ecr.aws/lambda/python@sha256:f7375fffebeaad02c20b440fa0ee2a5a813f1c6101252fd27ba6a0ce22600d2c
RUN yum install atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel -y
RUN pip install boto3
RUN pip install opensearch-py
RUN pip install requests
RUN pip install requests-aws4auth
COPY app.py ./
CMD [ "app.lambda_handler" ]
