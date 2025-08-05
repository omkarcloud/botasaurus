import React from "react";
import Admonition from "@theme-original/Admonition";

export default function AdmonitionWrapper(props) {
  if (props.title === "header") {
    return <Admonition {...props} icon={null} title="" />;
  }
  return <Admonition {...props} />;
}