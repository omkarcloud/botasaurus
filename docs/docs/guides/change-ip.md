---
sidebar_position: 10
---

# Changing IP [Must Read]

Changing your IP is of immense importance in bot development and web scraping as it helps prevent suspension and bypass IP blocks.

## Why Change IP?

I once read in a book, **"When your why is clear, the how is easy."** So, let's understand why you need to change your IP.

There are two most important reasons to change your IP:

**1. Preventing Suspension:** 
Imagine you create 100 accounts on LinkedIn using the same IP. Soon enough, LinkedIn will ask you for identity verification.

![LinkedIn Restricted Account](/img/linkedin-restricted.png)

LinkedIn restricts the account because it recognizes that 100 accounts were created using a single IP, indicating possible bot activity.

To avoid such restrictions, you need to change your IP each time the bot runs.

Remember, the golden rule to prevent suspension is **"No two bots should have the same IP."**

**2. Bypassing IP Blocks:** 
If you try to scrape fiverr.com, after a few page scrapes, you might encounter the following PerimeterX screen.

![Fiverr IP Block](/img/fiverr-block.webp)

In cases like these, when you get blocked, you need to change your IP to continue scraping.

## Methods for Changing IP

Here are five methods you can use to change your IP: 

**#1 Enable and Disable Airplane Mode**

In this method, you can utilize the connection between your PC and a mobile hotspot to access the internet via a SIM card. Then, enable and disable airplane mode on your mobile device to get a new IP.

This method is quite fast and usually takes 10 seconds to acquire a new IP.

Here's how you can enable and disable airplane mode to change your IP:

1. Connect your PC to a mobile hotspot.

2. On your mobile device, turn airplane mode on and off.

3. Now, turn the hotspot on again.

4. You will get a new IP assigned.

**#2 Restart Router**

For devices connected to a Wi-Fi network, turning off the router and then turning it back on will change the IP. It is a slow method, and the router will take 2-3 minutes to re-establish connection.

**#3 Use Proxies**
Paid services like BrightData, Oxylab, and IPRoyal provide a pool of residential IPes. However, they can be quite expensive, with prices averaging around $15 per GB for residential IPs.

If you opt for this method and are scraping large amounts of data, consider disabling the loading of CSS and images to reduce costs.

**#4 Use Tor Network**
The Tor network is a decentralized network that anonymizes your internet traffic by routing it through multiple volunteer-operated relays.

If you have access to a Windows device, you can use the [AnonSurf Application](https://github.com/ultrafunkamsterdam/AnonSurf) by ultrafunkamsterdam.

![AnonSurf Application](https://i.imgur.com/h1o0IEu.gif)

However, note that Tor IPs have a higher chance of being detected than home IPs.

**#5 Use VPN**

There are VPN services with free tiers like [WindScribe](https://windscribe.com/) and [ProtonVPN](https://protonvpn.com/).

You can use these VPN services to change your IP.

![WindScribe VPN](https://addons.mozilla.org/user-media/previews/full/267/267630.png?modified=1647977329)

Again, note that VPN IPs have a higher chance of being detected than home IPs.

## Which Method Should You Use?  
While we have outlined five methods for comprehensiveness

, in practical terms, for more than 90% of cases involving small-scale scraping and automations, we recommend using the **"Enable and Disable Airplane Mode"** method.

It is a free, fast, and code-free method to obtain IPs with high reputation. This is my go-to method for acquiring IPs with high reputation.

For larger web scraping/automation tasks, such as scraping one million pages or creating 5000 accounts on a website, we recommend using proxies. If possible, consider disabling the loading of CSS and images to reduce costs.