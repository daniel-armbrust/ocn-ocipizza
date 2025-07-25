README.txt
----------

- GRU = Brasil / São Paulo (sa-saopaulo-1)
- VCP = Brasil / São Paulo (sa-saopaulo-1)

Arquivos do Tenancy-A 
=====================

- tenancy-a/
    - locals.tf
        -
    - datasource.tf
        - Data Source global.
    
    - gru_datasource.tf
    - vcp_datasource.tf
        - Data Source das regiões GRU e VCP.  

    - gru_vcn.tf
    - vcp_vcn.tf
        - VCNs das regiões GRU e VCP.

    - gru_subnet.tf
    - vcp_subnet.tf
        - Sub-redes das regiões GRU e VCP.

    - gru_subnet-routetable.tf
    - vcp_subnet-routetable.tf
        - Tabelas de Roteamento das sub-redes das regiões GRU e VCP.

    - gru_subnet-security.tf
    - vcp_subnet-security.tf
        - Security Lists das sub-redes das regiões GRU e VCP.
        
    - gru_dhcpoptions.tf
    - vcp_dhcpoptions.tf
        - DHCP Options das sub-redes das regiões GRU e VCP.
    
    - gru_gateways.tf
    - vcp_gateways.tf
        - Internet, NAT e Service Gateways das regiões GRU e VCP.
    
    - gru_localpeering.tf
    - vcp_localpeering.tf
        - Local Peering Gateways das regiões GRU e VCP.

    - gru_remotepeering.tf
    - vcp_remotepeering.tf
        - Remote Peering Gateways das regiões GRU e VCP.

    - gru_compute.tf
    - vcp_compute.tf
        - Máquinas Virtuais das regiões GRU e VCP.
    
    - gru_firewall.tf
    - vcp_firewall.tf
        - Firewall das regiões GRU e VCP.

    - gru_drg.tf
    - vcp_drg.tf
        - DRG e Attachments das regiões GRU e VCP.

    - gru_drg-routetable.tf
    - vcp_drg-routetable.tf
        - Tabelas de Roteamento do DRG das regiões GRU e VCP.

    - gru_bastion.tf
    - vcp_bastion.tf
        - Bastion das regiões GRU e VCP.

    - gru_mysql.tf
    - vcp_mysql.tf




