import React from 'react'
import clsx from 'clsx'
import Link from '@docusaurus/Link'
import useDocusaurusContext from '@docusaurus/useDocusaurusContext'
import Layout from '@theme/Layout'
import HomepageFeatures, { Inspired, Thanks } from '@site/src/components/HomepageFeatures'

import styles from './index.module.css'

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext()
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/tutorial/">
            Read Tutorial
          </Link>
          <iframe
            src="https://ghbtns.com/github-btn.html?user=omkarcloud&repo=bose&type=star&count=true&size=large"
            frameBorder={0}
            scrolling={'0'}
            width={170}
            height={30}
            title="GitHub"
            style={{ border: 0, colorScheme: "auto" }}
          />
        </div>
      </div>
    </header>
  )
}


export default function Home(): JSX.Element {
  return (
    <Layout
      title={`Bose Framework`}
      description="The Ultimate Web Scraping Framework">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        {/* <Inspired/>
        <Thanks/> */}
      </main>
    </Layout>
  )
}
