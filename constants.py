
# State names
LAST_ACK    = 'LAST_ACK'
CLOSE_WAIT  = 'CLOSE_WAIT'
TIME_WAIT   = 'TIME_WAIT'
CLOSING     = 'CLOSING'
FIN_WAIT_2  = 'FIN_WAIT_2'
FIN_WAIT_1  = 'FIN_WAIT_1'
ESTABLISHED = 'ESTABLISHED'
SYN_RCVD    = 'SYN_RCVD'
SYN_SENT    = 'SYN_SENT'
LISTEN      = 'LISTEN'
CLOSED      = 'CLOSED'

# Valid TCP events/inputs
TIMEOUT = 'TIMEOUT' # Passive Open
SDATA   = 'SDATA'   # Active Open
RDATA   = 'RDATA'   # Data received from networks
FIN     = 'FIN'     # FIN received
ACK     = 'ACK'     # ACK received
SYNACK  = 'SYNACK'  # SYN + ACK received
CLOSE   = 'CLOSE'   # Client or Server issues close()
SYN     = 'SYN'     # SYN received
ACTIVE  = 'ACTIVE'  # Active Open
PASSIVE = 'PASSIVE' # Passive Open