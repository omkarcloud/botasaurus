---
sidebar_position: 2
---

# macOS Code Signing Guide

To sign a macOS installer (.dmg), you need:

- A Mac  
- A subscription to the [Apple Developer Program](https://developer.apple.com/support/compare-memberships/), which costs $99 per year  

Once you have these, watch this detailed video to learn how to sign apps for macOS:

[![macOS Code Signing Example Video](https://raw.githubusercontent.com/omkarcloud/macos-code-signing-example/master/images/macos-code-signing-example-video.png)](https://www.youtube.com/watch?v=hYBLfjT57hU)

The video covers:  
- Enrolling in the Apple Developer Program  
- Creating a certificate  
- Configuring your app for code signing  
- Building and signing your app  
- Using GitHub Actions and S3 for upload  

:::info[Note]  
While the video demonstrates general Electron macOS signing, you will need to adjust the steps specifically for Botasaurus Desktop, which is easy. A dedicated tutorial is coming soon.  
:::

:::tip[Tip]  
If you are a nonprofit organization or educational institution, you may qualify for Apple's Developer Program **fee waiver**. The waiver removes the $99 annual charge, saving you about $1,000 over a decade.

Check your eligibility and the [application process here](https://developer.apple.com/help/account/membership/fee-waivers/).  
:::