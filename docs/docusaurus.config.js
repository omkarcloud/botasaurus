// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require("prism-react-renderer/themes/github")
const darkCodeTheme = require("prism-react-renderer/themes/dracula")

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "🤖 Botasaurus Framework 🤖",
  tagline: "Botasaurus is a Swiss Army knife 🔪 for web scraping and browser automation 🤖 that helps you create bots fast. ⚡️",
  url: "https://www.omkar.cloud",
  trailingSlash: true,

  favicon: "img/favicon.ico",
  scripts: [
    {
      src: "https://www.googletagmanager.com/gtag/js?id=G-5QFML2CFEJ",
      async: true,
    },
    {
      src: "/botasaurus/ga.js",
    },
  ],
  baseUrl: "/botasaurus/",

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: "omkarcloud", // Usually your GitHub org/user name.
  projectName: "botasaurus", // Usually your repo name.

  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  presets: [
    [
      "classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve("./sidebars.js"),
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            "https://github.com/omkarcloud/botasaurus/blob/master/docs",
        },
        blog: false,
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      colorMode: {
        defaultMode: "dark",
        disableSwitch: false,
        respectPrefersColorScheme: false,
      },
      // Replace with your project's social card
      image: "img/twitter-card.png",
      navbar: {
        title: "Botasaurus",
        logo: {
          alt: "Botasaurus Logo",
          src: "https://raw.githubusercontent.com/omkarcloud/botasaurus/master/images/mascot-logo.png",
        },
        items: [
          {
            type: "docSidebar",
            sidebarId: "tutorialSidebar",
            position: "left",
            label: "Docs",
          },
          // {to: '/blog', label: 'Blog', position: 'left'},
          {
            href: "https://github.com/omkarcloud/botasaurus",
            label: "Love It? Star It! ★",
            position: "right",
          },
        ],
      },
      footer: {
        style: "dark",
        links: [
          {
            title: "Docs",
            items: [
              {
                label: "What is Botasaurus?",
                to: "/docs/what-is-botasaurus/",
              },
            ],
          },
          {
            title: "Community",
            items: [
              // {
              //   label: 'Stack Overflow',
              //   href: 'https://stackoverflow.com/questions/tagged/botasaurus',
              // },
              {
                label: "GitHub Discuss",
                href: "https://github.com/omkarcloud/botasaurus/discussions",
              },
            ],
          },
          {
            title: "More",
            items: [
              // {
              //   label: 'Blog',
              //   to: '/blog',
              // },
              {
                label: "GitHub",
                href: "https://github.com/omkarcloud/botasaurus",
              },
            ],
          },
        ],
        copyright: `Made in Bharat 🇮🇳 - Vande Mataram`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
      },
    }),
}

module.exports = config
