import Link from '@docusaurus/Link'
import React from 'react'
import clsx from 'clsx'
import styles from './styles.module.css'

type FeatureItem = {
  title: string
  Svg: React.ComponentType<React.ComponentProps<'svg'>>
  description: any
}

const FeatureList: FeatureItem[] = [
  {
    title: 'Anti-blocking',
    Svg: require('@site/static/img/undraw_mountain.svg').default,
    description: (
      <>
      Botasaurus adds <strong>anti-blocking</strong> features and <strong>common user agents</strong> to evade blocking from Cloudflare, PerimeterX, and other anti-bot services.
      </>
    ),
  },
  {
    title: 'Helpful Utils',
    Svg: require('@site/static/img/undraw_tree.svg').default,
    description: (
      <>
        Botasaurus includes tools for <strong>account generation</strong>, <strong>temporary email</strong>, and <strong>saving data as CSV/JSON</strong> and many more.
      </>
    ),
  },
  {
    title: 'Debug Support',
    Svg: require('@site/static/img/undraw_react.svg').default,
    description: (
      <>
        Botasaurus automatically prevents the browser from closing when an exception occurs, making it easier to debug your scripts.</>
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



export default function HomepageFeatures(): any {
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
