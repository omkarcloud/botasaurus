import React from "react"
import clsx from "clsx"
import TOCItems from "@theme/TOCItems"
import styles from "./styles.module.css"
// Using a custom className
// This prevents TOCInline/TOCCollapsible getting highlighted by mistake
const LINK_CLASS_NAME = "table-of-contents__link toc-highlight"
const LINK_ACTIVE_CLASS_NAME = "table-of-contents__link--active"
export default function TOC({ className, ...props }) {
  return (
    <div className={clsx(styles.tableOfContents, "thin-scrollbar", className)}>
      <TOCItems
        {...props}
        linkClassName={LINK_CLASS_NAME}
        linkActiveClassName={LINK_ACTIVE_CLASS_NAME}
      />
      <ul className="table-of-contents table-of-contents__left-border">
        <li>
            <strong>Sponsors</strong>
        </li>
        <li>
          <a
            href="https://www.omkar.cloud/l/bright-data/"
            className="table-of-contents__link toc-highlight"
          >
            <img src="https://www.omkar.cloud/images/bright-data-banner.png"/>
          </a>
        </li>
      </ul>
    </div>
  )
}
