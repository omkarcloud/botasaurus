---
sidebar_position: 30
---
# User Agent

The UserAgent provides a set of commonly used pre-defined user agents for web browsers. It also provides two class-level constants, RANDOM and HASHED.

Class Attributes
----------------

-   `RANDOM`: A string constant that can be used to indicate a randomly selected user agent. When using the RANDOM user agent, we mimic real-world user agents in a way that the probability of getting a user agent is consistent with real-world usage. This behavior aligns with your expectations.
-   `HASHED`: A string constant that can be used to indicate a hashed user agent based on the profile passed to BrowserConfig. When using the HASHED user agent, we mimic real-world user agents in a way that the probability of getting a user agent is consistent with real-world usage. This behavior aligns with your expectations.
-   `user_agent_106`: Represents user agent of Chrome 106
-   `user_agent_105`: Represents user agent of Chrome 105
-   `user_agent_104`: Represents user agent of Chrome 104
-   `user_agent_103`: Represents user agent of Chrome 103
-   `user_agent_101`: Represents user agent of Chrome 101
-   `user_agent_100`: Represents user agent of Chrome 100
-   `user_agent_99`: Represents user agent of Chrome 99
-   `user_agent_98`: Represents user agent of Chrome 98
-   `user_agent_97`: Represents user agent of Chrome 97
-   `user_agent_96`: Represents user agent of Chrome 96
-   `user_agent_95`: Represents user agent of Chrome 95
-   `user_agent_94`: Represents user agent of Chrome 94

user agent class is used to denote the user agent to use when running the browser. The default user agent is 1920x1080. 

Usage
-----
UserAgent in used when specifying the BrowserConfig in Task. 

For example the following example specifies to use user agent 106 on each run of Task.

```python
from bose import BaseTask, BrowserConfig, UserAgent

class Task(BaseTask):
    browser_config = BrowserConfig(user_agent=UserAgent.user_agent_106)
```

Note the following default behaviours:
- If you do not specify a user agent, the Task will run with a random UserAgent on each run by default. This means that the user agent can be different for each run, for example, Chrome 104 on the first run and Chrome 96 on the next run. This behavior is equivalent to a RANDOM selection.

- If you have provided a profile but do not specify a user agent, the Task will run with a user agent that remains the same on each run for that particular profile. For instance, if you are running a task with profile '1' and the selected user agent based on the profile is Chrome 104, then the user agent will remain as Chrome 104 for every run of the task associated with profile '1'. This behavior is similar to a HASHED selection.

These are smart defaults choosen in line with your expectations.