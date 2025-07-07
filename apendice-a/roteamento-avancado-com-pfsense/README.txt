README.txt
----------

- GRU = Brasil / São Paulo (sa-saopaulo-1)
- VCP = Brasil / São Paulo (sa-saopaulo-1)

Arquivos do Tenancy-A 
=====================

- tenancy-a/
    - datasource.tf
        -
    
    - locals.tf
        -

    - gru_vcn.tf
    - vcp_vcn.tf
        - VCNs da região GRU e VCP.

    - gru_subnet.tf
    - vcp_subnet.tf
        - Sub-redes da região GRU e VCP.

    - gru_subnet-routetable.tf
    - vcp_subnet-routetable.tf
        - Tabelas de Roteamento das sub-redes da região GRU e VCP.

    - gru_subnet-security.tf
    - vcp_subnet-security.tf
        - Security Lists das sub-redes da região GRU e VCP.
        
    - gru_dhcpoptions.tf
    - vcp_dhcpoptions.tf
        - DHCP Options das sub-redes da região GRU e VCP.
    
    - gru_gateways.tf
    - vcp_gateways.tf
        - Internet, NAT e Service Gateways da região GRU e VCP.
    
    - gru_localpeering.tf
    - vcp_localpeering.tf
        - Local Peering Gateways da região GRU e VCP.

    - gru_remotepeering.tf
    - vcp_remotepeering.tf
        - Remote Peering Gateways da região GRU e VCP.

    - gru_compute.tf
    - vcp_compute.tf
        - Máquinas Virtuais da região GRU e VCP.

    - gru_drg.tf
    - vcp_drg.tf
        - DRG e Attachments da região GRU e VCP.

    - gru_drg-routetable.tf
    - vcp_drg-routetable.tf
        - Tabelas de Roteamento do DRG da região GRU e VCP.




