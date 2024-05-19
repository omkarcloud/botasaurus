class BrowserResourceConfig:
    AVERAGE_RICH_MEDIA_SITE = 0.5  # 0.5 GB like omkar.cloud (Most Common) 
    STATIC_SIMPLE_SITE = 0.3  # 0.3 GB like stackoverflow.com
    VIDEO_SITE = 0.8  # 0.8 GB like youtube.com, udemy.com

def calc_max_parallel_browsers(average_ram_per_instance = BrowserResourceConfig.AVERAGE_RICH_MEDIA_SITE, min=1, max=None):
        """
        Calculate the maximum number of browser instances that can be run simultaneously on a PC.

        :param average_ram_per_instance: The average RAM usage per Chrome instance in GB.
                                     This value can vary based on the type of website being accessed:
                                     - Average Rich Media Site like omkar.cloud: 0.5 GB
                                     - Static Simple Site like moralstories26.com: 0.3 GB
                                     - Video Site like youtube.com, udemy.com: 0.8 GB
        :return: The maximum number of browser instances that can be run simultaneously.
        """
        from psutil import virtual_memory
        # System available resources
        available_ram = virtual_memory().available / (1024 ** 3)  # Convert bytes to GB

        # Validate input
        if average_ram_per_instance <= 0:
            raise ValueError("Average RAM per instance must be a positive number.")
        

        if 0.3 <= available_ram and available_ram <= 1.3 :
            return 1
        
        RAM_FOR_OS_PROCESS = 0.8 # 0.8 GB for OS and other processes
        
        # Calculate maximum instances based on available RAM
        max_instances_ram = (((available_ram - RAM_FOR_OS_PROCESS) / average_ram_per_instance))   

        # The limiting factor is determined by the available RAM
        max_instances = int(max_instances_ram)

        if min:
            if max_instances <= min:
                return min

        if max:
            if max_instances >= max:
                return max
        
        return max_instances
