from .base_data import BaseData
from .utils import is_windows, is_mac

def get_correct_agent(windows, mac, linux):
    if is_windows():
        return windows
    elif is_mac():
        return mac
    else:
        return linux

class UserAgent(BaseData):

    RANDOM = "RANDOM"
    HASHED = "HASHED"

    user_agent_106 = get_correct_agent("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.37",
                                       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
                                       "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.37")

    user_agent_105 = get_correct_agent("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
                                       "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
                                       "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36")

    user_agent_104 = get_correct_agent("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36",
                                       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
                                       "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36")

    user_agent_103 = get_correct_agent("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
                                       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
                                       "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36")

    user_agent_101 = get_correct_agent("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951 Safari/537.36",
                                       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.0 Safari/537.36",
                                       "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951 Safari/537.36"
                                       )

    user_agent_100 = get_correct_agent("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896 Safari/537.36",
                                       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.62 Safari/537.36",
                                       "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896 Safari/537.36"
                                       )

    user_agent_99 = get_correct_agent("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844 Safari/537.36",
                                      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
                                      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844 Safari/537.36"
                                      )

    user_agent_98 = get_correct_agent("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758 Safari/537.36",
                                      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
                                      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758 Safari/537.36"
                                      )

    user_agent_97 = get_correct_agent("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692 Safari/537.36",
                                      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
                                      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692 Safari/537.36"
                                      )

    user_agent_96 = get_correct_agent("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664 Safari/537.36",
                                      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
                                      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664 Safari/537.36"
                                      )

    user_agent_95 = get_correct_agent("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638 Safari/537.36",
                                      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
                                      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638 Safari/537.36"
                                      )

    user_agent_94 = get_correct_agent("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606 Safari/537.36",
                                      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
                                      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606 Safari/537.36")

    def get_data(self):
        # Versions
        V_106 = 37
        V_105 = 42
        V_104 = 2
        V_103 = 2
        V_101 = 1
        V_99 = 10
        V_100 = 1
        V_98 = 1
        V_97 = 1
        V_96 = 1
        V_95 = 1
        V_94 = 1

        _106 = [self.user_agent_106] * V_106
        _105 = [
            self.user_agent_105] * V_105
        _104 = [
            self.user_agent_104] * V_104
        _103 = [
            self.user_agent_103] * V_103
        _101 = [
            self.user_agent_101] * V_101
        _99 = [
            self.user_agent_99] * V_99
        _100 = [
            self.user_agent_100] * V_100
        _98 = [
            self.user_agent_98] * V_98
        _97 = [
            self.user_agent_97] * V_97
        _96 = [
            self.user_agent_96] * V_96
        _95 = [
            self.user_agent_95] * V_95
        _94 = [self.user_agent_94] * V_94

        result = _106 + _105 + _104 + _103 + \
            _101 + _99 + _100 + _98 + _97 + _96 + _95 + _94

        return result


UserAgentInstance = UserAgent()
if __name__ == '__main__':
    UserAgentInstance = UserAgent()
    print(UserAgentInstance.get_hashed('a'))
    print(UserAgentInstance.get_hashed('a'))
    print(UserAgentInstance.get_hashed('b'))
