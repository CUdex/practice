from pythonping import ping
import ipaddress
import psutil
import wmi

def get_network_id(ip_str, ip_netmask):
    ip_address = ipaddress.ip_interface(ip_str + "/" + ip_netmask)
    
    # network id 획득
    return ipaddress.ip_network(ip_address.network).network_address

def get_default_gateway():
    try:
        wmi_obj = wmi.WMI()
        wmi_sql = "select DefaultIPGateway from Win32_NetworkAdapterConfiguration where IPEnabled=TRUE"
        wmi_out = wmi_obj.query( wmi_sql )

        return wmi_out[0].DefaultIPGateway[0]
    
    except Exception as e:
        print("기본 게이트웨이를 가져오는 중 오류 발생:", e)
        return None

def get_main_active_interface():
    try:
        # 활성 네트워크 인터페이스의 정보 가져오기
        active_nic_info = psutil.net_if_addrs()
        
        # default gateway 정보 가져오기
        default_gateway = get_default_gateway()

        # 네트워크 상태가 UP이고 주소가 할당된 인터페이스를 찾음
        for interface in active_nic_info.items():
            for addr in interface[1]:
                # 2는 IPv4를 의미하는 상수를 이용하여 IPv4를 사용하는 인터페이스인지 구별
                if addr.family == 2:
                    addr_id = get_network_id(addr.address, addr.netmask)
                    default_id = get_network_id(default_gateway, addr.netmask)

                    # default gateway와 network id가 같은 경우 해당 IP와 netmask를 반환
                    if addr_id == default_id:
                        # IP 및 subnet mask 값 반환
                        return addr.address, addr.netmask
        return None
    except Exception as e:
        print("main interface 값을 가져오는 중 오류 발생:", e)
        return None

def get_ip_range():
    try:
        # IP 및 netmask 획득
        ip_str, netmask_str = get_main_active_interface()

        hosts = ip_str + '/' + netmask_str

        network = ipaddress.IPv4Network(hosts, strict=False)

        # 해당 서브넷의 IP 범위를 문자열 리스트로 반환
        ip_range_list = [str(ip) for ip in network.hosts()]

        # hosts에서 자신의 IP 제거
        ip_range_list.remove(ip_str)
        
        return ip_range_list
    
    except Exception as e:
        print("IP 범위를 가져오는 중 오류 발생:", e)
        return []
    
if __name__ == '__main__':
    ip_list = []
    ping_list = get_ip_range()
    for ip in ping_list:
        result = ping(target=ip, timeout=1, count=1, verbose=False)
        result = str(result)
        if 'Reply' in result:
            print(f'{ip} > success')
            ip_list.append(ip)
        else: print(f'{ip} > fail')
    print(ip_list)