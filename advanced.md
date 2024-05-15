## 🤔 Advanced Questions

### How to Run Botasaurus in Google Colab?

1. Run the following code snippet to install Chrome and Botasaurus:

```python
! apt-get update
! wget  https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
! apt-get install -y lsof wget gnupg2 apt-transport-https ca-certificates software-properties-common adwaita-icon-theme alsa-topology-conf alsa-ucm-conf at-spi2-core dbus-user-session dconf-gsettings-backend dconf-service fontconfig fonts-liberation glib-networking glib-networking-common glib-networking-services gsettings-desktop-schemas gtk-update-icon-cache hicolor-icon-theme libasound2 libasound2-data libatk-bridge2.0-0 libatk1.0-0 libatk1.0-data libatspi2.0-0 libauthen-sasl-perl libavahi-client3 libavahi-common-data libavahi-common3 libcairo-gobject2 libcairo2 libclone-perl libcolord2 libcups2 libdata-dump-perl libdatrie1 libdconf1 libdrm-amdgpu1 libdrm-common libdrm-intel1 libdrm-nouveau2 libdrm-radeon1 libdrm2 libencode-locale-perl libepoxy0 libfile-basedir-perl libfile-desktopentry-perl libfile-listing-perl libfile-mimeinfo-perl libfont-afm-perl libfontenc1 libgbm1 libgdk-pixbuf-2.0-0 libgdk-pixbuf2.0-bin libgdk-pixbuf2.0-common libgl1 libgl1-mesa-dri libglapi-mesa libglvnd0 libglx-mesa0 libglx0 libgraphite2-3 libgtk-3-0 libgtk-3-bin libgtk-3-common libharfbuzz0b libhtml-form-perl libhtml-format-perl libhtml-parser-perl libhtml-tagset-perl libhtml-tree-perl libhttp-cookies-perl libhttp-daemon-perl libhttp-date-perl libhttp-message-perl libhttp-negotiate-perl libice6 libio-html-perl libio-socket-ssl-perl libio-stringy-perl libipc-system-simple-perl libjson-glib-1.0-0 libjson-glib-1.0-common liblcms2-2 libllvm11 liblwp-mediatypes-perl liblwp-protocol-https-perl libmailtools-perl libnet-dbus-perl libnet-http-perl libnet-smtp-ssl-perl libnet-ssleay-perl libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 libpciaccess0 libpixman-1-0 libproxy1v5 librest-0.7-0 librsvg2-2 librsvg2-common libsensors-config libsensors5 libsm6 libsoup-gnome2.4-1 libsoup2.4-1 libtext-iconv-perl libthai-data libthai0 libtie-ixhash-perl libtimedate-perl libtry-tiny-perl libu2f-udev liburi-perl libvte-2.91-0 libvte-2.91-common libvulkan1 libwayland-client0 libwayland-cursor0 libwayland-egl1 libwayland-server0 libwww-perl libwww-robotrules-perl libx11-protocol-perl libx11-xcb1 libxaw7 libxcb-dri2-0 libxcb-dri3-0 libxcb-glx0 libxcb-present0 libxcb-randr0 libxcb-render0 libxcb-shape0 libxcb-shm0 libxcb-sync1 libxcb-xfixes0 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxft2 libxi6 libxinerama1 libxkbcommon0 libxkbfile1 libxml-parser-perl libxml-twig-perl libxml-xpathengine-perl libxmu6 libxmuu1 libxrandr2 libxrender1 libxshmfence1 libxt6 libxtst6 libxv1 libxxf86dga1 libxxf86vm1 libz3-4 mesa-vulkan-drivers perl-openssl-defaults shared-mime-info termit x11-common x11-utils xdg-utils xvfb
! dpkg -i google-chrome-stable_current_amd64.deb
! python -m pip install botasaurus
```

![install-chrome-colab](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/install-chrome-colab.png)

2. Next, test Botasaurus by running this code snippet:

```python
from botasaurus.browser import browser, Driver

@browser
def scrape_heading_task(driver: Driver, data):
    driver.google_get("https://www.g2.com/products/jenkins/reviews?page=5", bypass_cloudflare=True)
    heading = driver.get_text('.product-head__title [itemprop="name"]')
    driver.save_screenshot()
    return heading

scrape_heading_task()
```

![bota-test](https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/bota-test.png)

## Love It? [Star It! ⭐](https://github.com/omkarcloud/botasaurus)

Become one of our amazing stargazers by giving us a star ⭐ on GitHub!

It's just one click, but it means the world to me.

<a href="https://github.com/omkarcloud/botasaurus/stargazers">
    <img src="https://bytecrank.com/nastyox/reporoster/php/stargazersSVG.php?user=omkarcloud&repo=botasaurus" alt="Stargazers for @omkarcloud/botasaurus">
</a>
