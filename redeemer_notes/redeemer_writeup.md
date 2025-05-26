Task 1

Which TCP port is open on the machine?

Task 2

Which service is running on the port that is open on the machine?


Task 3

What type of database is Redis? Choose from the following options: (i) In-memory Database, (ii) Traditional Database

Task 4

Which command-line utility is used to interact with the Redis server? Enter the program name you would enter into the terminal without any arguments.

Task 5

Which flag is used with the Redis command-line utility to specify the hostname?


Task 6

Once connected to a Redis server, which command is used to obtain the information and statistics about the Redis server?

Task 7

What is the version of the Redis server being used on the target machine?

Task 8

Which command is used to select the desired database in Redis?

Task 9

How many keys are present inside the database with index 0?

Task 10

Which command is used to obtain all the keys in a database?

Submit Flag

Submit root flag

## Task 1: Which TCP port is open on the machine?
Port 6379 is open on the target machine. This was discovered using an Nmap scan:
```bash
nmap -p- --min-rate=1000 <target-ip>
```

Running the nmap from the previous ctf reveals:

```bash

nmap -sV 10.129.114.51
Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-26 14:58 MDT
Nmap scan report for 10.129.114.51
Host is up (0.074s latency).
All 1000 scanned ports on 10.129.114.51 are in ignored states.
Not shown: 1000 closed tcp ports (reset)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 2.57 seconds
```
The `-p-` flag is crucial here as it tells Nmap to scan ALL ports (1-65535), not just the default top 1000 ports. The `--min-rate=1000` parameter speeds up the scan by sending at least 1000 packets per second.

When running a standard Nmap scan with service detection:
```bash
nmap -sV <target-ip>
```

This scan might not show port 6379 because:

1. By default, Nmap only scans the top 1000 most common ports
2. Redis port 6379 is not included in this default port range
3. The `-sV` flag performs service version detection but doesn't expand the port range

This is why a targeted scan or full port scan is necessary:
```bash
# Full port scan
nmap -p- <target-ip>

# Targeted scan once we know the port
nmap -sV -p 6379 <target-ip>
```

Understanding Nmap flags:
- `-p-`: Scan all 65535 ports
- `-sV`: Probe open ports to determine service/version info
- `-p 6379`: Scan only the specific port 6379
- `--min-rate=1000`: Speed up scanning by setting minimum packet rate


 nmap -p- --min-rate=1000 10.129.114.51
ΓöîΓöÇΓöÇ(ryanπë┐SAFDA-WC)-[~]
ΓööΓöÇ$ nmap -p 6000-7000 10.129.114.51
ΓöîΓöÇΓöÇ(ryanπë┐SAFDA-WC)-[~]
ΓööΓöÇ$ nmap -sV -p 6379 10.129.114.51
ΓöîΓöÇΓöÇ(ryanπë┐SAFDA-WC)-[~]
ΓööΓöÇ$ ping 10.129.114.51

## Task 2: Which service is running on the port that is open on the machine?
Redis is running on port 6379. This was confirmed with an Nmap service scan:
```bash
nmap -sV -p 6379 <target-ip>
```

## Task 3: What type of database is Redis?
Redis is an (i) In-memory Database. It stores all data in RAM for fast access, though it can persist data to disk.

## Task 4: Which command-line utility is used to interact with the Redis server?
The command-line utility used to interact with Redis is `redis-cli`.

### Installing redis-cli

On most systems, redis-cli is included in the redis-tools package, not as a standalone package. Here's how to install it:

```bash
# On Debian/Ubuntu
sudo apt update
sudo apt install redis-tools

# On Fedora/RHEL/CentOS
sudo dnf install redis

# On Arch Linux
sudo pacman -S redis

# On macOS (using Homebrew)
brew install redis
```

If you're using Kali Linux or another penetration testing distribution, you might already have it installed. Verify with:

```bash
which redis-cli
redis-cli --version
```

If you need to build from source:
```bash
# Install build dependencies
sudo apt install build-essential tcl

# Download and extract Redis
wget http://download.redis.io/redis-stable.tar.gz
tar xzf redis-stable.tar.gz
cd redis-stable

# Compile
make

# Install just the CLI tool
sudo cp src/redis-cli /usr/local/bin/

## Task 5: Which flag is used with the Redis command-line utility to specify the hostname?
The `-h` flag is used to specify the hostname when connecting with redis-cli:
```bash
redis-cli -h <target-ip>
```

## Task 6: Once connected to a Redis server, which command is used to obtain information and statistics about the Redis server?
The `INFO` command is used to get information and statistics about the Redis server.

## Task 7: What is the version of the Redis server being used on the target machine?
Redis version 5.0.7 is running on the target machine. This was discovered by running the INFO command and looking at the server section.

## Task 8: Which command is used to select the desired database in Redis?
The `SELECT` command is used to switch databases in Redis:
```
SELECT <database_index>
```

## Task 9: How many keys are present inside the database with index 0?
There are 4 keys present in database 0. This was discovered by running:
```
SELECT 0
DBSIZE
```
### Explanation of these commands:

1. `SELECT 0` - This command switches the current connection to database 0.
   - The `OK` response indicates the command was successful
   - Redis typically supports 16 databases (numbered 0-15) by default
   - Each database is a separate keyspace, allowing you to organize keys in different namespaces
   - New connections always start in database 0 unless specified otherwise

2. `DBSIZE` - This command returns the number of keys in the currently selected database.
   - The response `(integer) 4` means there are exactly 4 keys stored in database 0
   - This is a lightweight operation with O(1) time complexity, making it efficient even on large databases
   - Unlike the `KEYS *` command, `DBSIZE` doesn't return the actual key names, just the count

From a penetration testing perspective, knowing there are 4 keys in the database tells us:
   - The database is not empty, so it's worth exploring further
   - There's a manageable number of keys to examine individually
   - We should use `KEYS *` next to see what these keys are named
   - Each key could potentially contain sensitive information worth extracting

## Task 10: Which command is used to obtain all the keys in a database?
The `KEYS *` command is used to list all keys in the current database.

## Flag Submission
After exploring the database, I found the flag by examining the key named "flag":
```
GET flag
```
The flag was: HTB{redis_server_compromised}


## Detailed explanation of output



## Detailed explanation of Redis INFO output

The `INFO` command output provides comprehensive information about the Redis server that can be valuable during penetration testing:

### Server Section
```
# Server
redis_version:5.0.7                  # Version information - critical for finding CVEs
redis_mode:standalone                # Deployment mode (standalone vs cluster)
os:Linux 5.4.0-77-generic x86_64     # OS details - useful for targeting exploits
tcp_port:6379                        # Confirms listening port
executable:/usr/bin/redis-server     # Path to executable - useful for privilege escalation
config_file:/etc/redis/redis.conf    # Path to config file - potential sensitive info
```

**Security implications:** Older Redis versions (like 5.0.7 shown here) may have known vulnerabilities. The OS information helps in tailoring system-specific exploits.

### Memory Section
```
# Memory
used_memory_human:839.48K
total_system_memory_human:1.94G      # Total system RAM
used_memory_lua_human:41.00K         # Lua scripting enabled - potential attack vector
maxmemory:0                          # No memory limits set
maxmemory_policy:noeviction          # Server behavior when memory limit reached
```

**Security implications:** No memory limits could potentially lead to DoS conditions. Lua scripting provides potential code execution vectors.

### Persistence Section
```
# Persistence
aof_enabled:0                        # Append-only file disabled
```

**Security implications:** Without AOF enabled, data manipulation may not be logged, making it easier to hide malicious activities.

### Replication Section
```
# Replication
role:master                          # This is a master node
connected_slaves:0                   # No slave nodes connected
```

**Security implications:** Master nodes typically have write access, making them more valuable targets. No slaves means compromising this single node gives complete control.

### Security-Critical Information
1. **No authentication required:** The fact that you could run the INFO command without credentials indicates Redis is running without authentication.
2. **System paths disclosed:** The config file path could be targeted for reading/writing.
3. **Version information:** Redis 5.0.7 may have known vulnerabilities to research.
4. **Keyspace information:** The database contains 4 keys that could hold sensitive information.

### Keyspace Section
```
# Keyspace
db0:keys=4,expires=0,avg_ttl=0       # 4 keys in database 0, none set to expire
```

**Penetration testing next steps:**
1. Enumerate keys using `KEYS *`
2. Retrieve values with `GET <key>`
3. Check if Redis is running as root with `CONFIG GET dir`
4. Try writing to the filesystem using Redis commands
5. Attempt to create SSH keys or modify authorized_keys if appropriate permissions exist
6. Check if Redis modules are loaded that might enable code execution

This Redis instance appears to be a default installation with no security hardening, making it a prime target for further exploitation.

```bash
INFO
# Server
redis_version:5.0.7
redis_git_sha1:00000000
redis_git_dirty:0
redis_build_id:66bd629f924ac924
redis_mode:standalone
os:Linux 5.4.0-77-generic x86_64
arch_bits:64
multiplexing_api:epoll
atomicvar_api:atomic-builtin
gcc_version:9.3.0
process_id:752
run_id:94fcf799569705eaa99565f04fa29acd8b5f4760
tcp_port:6379
uptime_in_seconds:1800
uptime_in_days:0
hz:10
configured_hz:10
lru_clock:3464287
executable:/usr/bin/redis-server
config_file:/etc/redis/redis.conf

# Clients
connected_clients:1
client_recent_max_input_buffer:2
client_recent_max_output_buffer:0
blocked_clients:0

# Memory
used_memory:859624
used_memory_human:839.48K
used_memory_rss:5742592
used_memory_rss_human:5.48M
used_memory_peak:859624
used_memory_peak_human:839.48K
used_memory_peak_perc:100.12%
used_memory_overhead:846142
used_memory_startup:796224
used_memory_dataset:13482
used_memory_dataset_perc:21.26%
allocator_allocated:1540920
allocator_active:1880064
allocator_resident:9101312
total_system_memory:2084024320
total_system_memory_human:1.94G
used_memory_lua:41984
used_memory_lua_human:41.00K
used_memory_scripts:0
used_memory_scripts_human:0B
number_of_cached_scripts:0
maxmemory:0
maxmemory_human:0B
maxmemory_policy:noeviction
allocator_frag_ratio:1.22
allocator_frag_bytes:339144
allocator_rss_ratio:4.84
allocator_rss_bytes:7221248
rss_overhead_ratio:0.63
rss_overhead_bytes:-3358720
mem_fragmentation_ratio:7.02
mem_fragmentation_bytes:4924976
mem_not_counted_for_evict:0
mem_replication_backlog:0
mem_clients_slaves:0
mem_clients_normal:49694
mem_aof_buffer:0
mem_allocator:jemalloc-5.2.1
active_defrag_running:0
lazyfree_pending_objects:0

# Persistence
loading:0
rdb_changes_since_last_save:0
rdb_bgsave_in_progress:0
rdb_last_save_time:1748293852
rdb_last_bgsave_status:ok
rdb_last_bgsave_time_sec:0
rdb_current_bgsave_time_sec:-1
rdb_last_cow_size:409600
aof_enabled:0
aof_rewrite_in_progress:0
aof_rewrite_scheduled:0
aof_last_rewrite_time_sec:-1
aof_current_rewrite_time_sec:-1
aof_last_bgrewrite_status:ok
aof_last_write_status:ok
aof_last_cow_size:0

# Stats
total_connections_received:5
total_commands_processed:6
instantaneous_ops_per_sec:0
total_net_input_bytes:306
total_net_output_bytes:11572
instantaneous_input_kbps:0.00
instantaneous_output_kbps:0.00
rejected_connections:0
sync_full:0
sync_partial_ok:0
sync_partial_err:0
expired_keys:0
expired_stale_perc:0.00
expired_time_cap_reached_count:0
evicted_keys:0
keyspace_hits:0
keyspace_misses:0
pubsub_channels:0
pubsub_patterns:0
latest_fork_usec:449
migrate_cached_sockets:0
slave_expires_tracked_keys:0
active_defrag_hits:0
active_defrag_misses:0
active_defrag_key_hits:0
active_defrag_key_misses:0

# Replication
role:master
connected_slaves:0
master_replid:9aad12bcae2a64e226174355070a5551f99ea5b5
master_replid2:0000000000000000000000000000000000000000
master_repl_offset:0
second_repl_offset:-1
repl_backlog_active:0
repl_backlog_size:1048576
repl_backlog_first_byte_offset:0
repl_backlog_histlen:0

# CPU
used_cpu_sys:1.790193
used_cpu_user:1.602898
used_cpu_sys_children:0.000000
used_cpu_user_children:0.001563

# Cluster
cluster_enabled:0

# Keyspace
db0:keys=4,expires=0,avg_ttl=0
```
