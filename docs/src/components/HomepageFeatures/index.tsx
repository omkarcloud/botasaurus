import Link from '@docusaurus/Link'
import React from 'react'
import clsx from 'clsx'
import styles from './styles.module.css'

type FeatureItem = {
  title: string
  Svg: React.ComponentType<React.ComponentProps<'svg'>>
  description: JSX.Element
}

const FeatureList: FeatureItem[] = [
  {
    title: 'Easy to Use',
    Svg: require('@site/static/img/undraw_mountain.svg').default,
    description: (
      <>
        Bose was designed from the ground up to be easily installed and
        get you up and scrape even the complex of sites.
      </>
    ),
  },
  {
    title: 'Focus on What Matters',
    Svg: require('@site/static/img/undraw_tree.svg').default,
    description: (
      <>
        Bose lets you focus on scraping, and we&apos;ll do boring bootstrap, logging and debugging.
      </>
    ),
  },
  {
    title: 'Powered by Selenium',
    Svg: require('@site/static/img/undraw_react.svg').default,
    description: (
      <>
        We have extended Selenium to make it really easy to scrape websites.      </>
    ),
  },
]

function Feature({ title, Svg, description }: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  )
}


export function Inspired(): JSX.Element {
  return (
    <section className={styles.inspired}>
      <div className="container">
        <h1 className="hero__title">{'Inspiration'}</h1>
        <div style={{ textAlign: 'left' }} >
          <p>We dedicate this project to Subhash Chandra Bose, the
            person who turbo boosted Bharat&#x27;s freedom. Subhash Chandra Bose was the founder of Azad Hind Fauj
            (Indian National Army),which was formed from Indian prisoners of war captured by the Axis powers
            (Germany, Japan, and Italy) during World War II. The Azad Hind Fauj fought against the British Indian
            Army to free Bharat from British rule in present day Mynammar.</p>
          <p>Although the Azad Hind Fauj was unsuccessful in
            defeating the British Indian Army, taking up arms against the British had a domino effect on Indians in
            the police and British Indian Army. They revolted and started fighting against the Britishers, forcing
            them to leave Bharat in 1947.</p>
          <p>Without Subhash Chandra Bose&#x27;s efforts, Bharat may
            have had to wait for few more decades to gain independence. Consequently, Internet would had
            arrived late in Bharat and, I wouldn&#x27;t have been able to learn programming and create this framework to
            help you.</p>
          <p>Therefore, we are grateful to Netaji for his role in
            turbo boosting Bharat&#x27;s freedom movement. Jai Hind.</p>
        </div>
      </div>
    </section>
  )
}


export function Thanks(): JSX.Element {
  return (
    <section className={styles.inspired}>
      <div className="container">
        <h1 className="hero__title">{'Thanks'}</h1>
        <div style={{ textAlign: 'left' }} className="page-body">
          <p className="">
            Bose framework stands on the shoulders of giants. We leverage various
            projects to simplify web scraping for you. We extend our gratitude to the
            following individuals who have developed the software that Bose framework
            relies on:
          </p>
          <ul className="bulleted-list">
            <li style={{ listStyleType: "disc" }}>
              Jason Huggins, the creator of the Selenium library, which is the backbone
              of Bose framework. Thank you, Jason, for creating Selenium.
            </li>
            <li style={{ listStyleType: "disc" }}>
              Leon, who developed the undetected-chromedriver library, which we utilize
              to avoid detection by anti-bot detection services such as Cloudflare.
              Thank you, Leon.
            </li>

            <li style={{ listStyleType: "disc" }}>
              Chida, who developed the chromedriver-autoinstaller library, which we
              employ to download the driver for your Chrome version that is utilized to
              launch the browser. Thank you, Chida.
            </li>
            <li style={{ listStyleType: "disc" }}>
              Eric Gazoni and Charlie Clark, who created the openpyxl library, which we
              utilize to save data as Excel files. Thank you, Eric Gazoni and Charlie
              Clark, for creating openpyxl.
            </li>
            <li style={{ listStyleType: "disc" }}>
              Kenneth Reitz, who developed the requests library, which is used in Bose
              framework. Thank you, Kenneth Reitz, for creating requests.
            </li>
          </ul>

        </div>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/tutorial/">
            Read Tutorial
          </Link>
        </div>
      </div>
    </section>
  )
}


export default function HomepageFeatures(): JSX.Element {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  )
}
