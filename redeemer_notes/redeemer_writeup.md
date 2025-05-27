# CTF Report: Redeemer

## Introduction

This report documents the completion of the Redeemer challenge from Hack The Box. Through this exercise, participants will gain knowledge and practical experience in:

- Network scanning and port discovery
- Redis database fundamentals
- Command-line interaction with Redis servers
- Database enumeration techniques
- Redis command syntax and usage

## Task Breakdown

### Task 1: Which TCP port is open on the machine?

**Question:** Which TCP port is open on the machine?

**Solution:**
```bash
nmap -p- --min-rate=1000 10.129.114.51
```

This command performs a full port scan of all 65535 ports with a minimum packet rate of 1000 packets per second, allowing us to discover non-standard open ports that might be missed by default scans.

**Importance:** This task demonstrates the importance of thorough port scanning in penetration testing. The default Nmap scan only checks the top 1000 ports, but Redis typically runs on port 6379, which isn't included in that range.

### Task 2: Which service is running on the port that is open on the machine?

**Question:** Which service is running on the port that is open on the machine?

**Solution:**
```bash
nmap -sV -p 6379 10.129.114.51
```

This command performs service version detection specifically on port 6379, allowing us to identify that Redis is running on this port.

**Importance:** Service identification is crucial for targeting our approach. Knowing that Redis is running gives us direction on which tools and techniques to use next.

### Task 3: What type of database is Redis?

**Question:** What type of database is Redis? Choose from the following options: (i) In-memory Database, (ii) Traditional Database

**Solution:**
Redis is an (i) In-memory Database.

**Importance:** Understanding Redis's nature as an in-memory database helps explain its performance characteristics and potential security implications. In-memory databases keep data primarily in RAM, making them fast but potentially vulnerable to data loss.

### Task 4: Which command-line utility is used to interact with the Redis server?

**Question:** Which command-line utility is used to interact with the Redis server? Enter the program name you would enter into the terminal without any arguments.

**Solution:**
```bash
redis-cli
```

This is the standard command-line interface for interacting with Redis servers.

**Importance:** Knowing the proper tools for interacting with services is essential for both administrators and penetration testers. The redis-cli utility provides direct access to all Redis functionality.

### Task 5: Which flag is used with the Redis command-line utility to specify the hostname?

**Question:** Which flag is used with the Redis command-line utility to specify the hostname?

**Solution:**
```bash
redis-cli -h 10.129.114.51
```

The `-h` flag specifies the hostname or IP address of the Redis server to connect to.

**Importance:** Understanding command-line parameters is crucial for connecting to remote services. This knowledge allows us to target specific Redis instances on a network.

### Task 6: Once connected to a Redis server, which command is used to obtain information and statistics about the Redis server?

**Question:** Once connected to a Redis server, which command is used to obtain the information and statistics about the Redis server?

**Solution:**
```
INFO
```

The INFO command returns detailed information about the Redis server instance, including version, memory usage, and configuration details.

**Importance:** Reconnaissance is a critical phase in penetration testing. The INFO command provides valuable system information that can help identify vulnerabilities or misconfigurations.

### Task 7: What is the version of the Redis server being used on the target machine?

**Question:** What is the version of the Redis server being used on the target machine?

**Solution:**
```
INFO
```

Looking at the server section of the INFO output reveals Redis version 5.0.7.

**Importance:** Version information is crucial for identifying potential vulnerabilities. Older versions of software often have known security issues that can be exploited.

### Task 8: Which command is used to select the desired database in Redis?

**Question:** Which command is used to select the desired database in Redis?

**Solution:**
```
SELECT 0
```

The SELECT command switches the current connection to the specified database index.

**Importance:** Redis supports multiple databases within a single instance. Understanding how to navigate between them is essential for thorough enumeration of the target.

### Task 9: How many keys are present inside the database with index 0?

**Question:** How many keys are present inside the database with index 0?

**Solution:**
```
SELECT 0
DBSIZE
```

These commands switch to database 0 and return the number of keys in that database (4).

**Importance:** Knowing the size of a database helps gauge its importance and the potential value of its contents. This step is crucial for focusing our enumeration efforts.

### Task 10: Which command is used to obtain all the keys in a database?

**Question:** Which command is used to obtain all the keys in a database?

**Solution:**
```
KEYS *
```

The KEYS command with the wildcard pattern (*) returns all key names in the current database.

**Importance:** This command allows us to discover what data is stored in the Redis instance, which is essential for finding sensitive information or potential attack vectors.

### Flag Submission: Submit root flag

**Question:** Submit root flag

**Solution:**
```
GET flag
```

After discovering the key named "flag" using the KEYS command, we use GET to retrieve its value, which contains the flag.

**Importance:** This final step demonstrates the importance of methodical enumeration. By systematically exploring the Redis instance, we were able to locate and extract the target data.

## Appendix: Command Outputs

### Nmap Scan Output
```
nmap -sV 10.129.114.51
Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-26 14:58 MDT
Nmap scan report for 10.129.114.51
Host is up (0.074s latency).
All 1000 scanned ports on 10.129.114.51 are in ignored states.
Not shown: 1000 closed tcp ports (reset)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 2.57 seconds
```

**Key observations:**
- The default scan shows no open ports in the top 1000 ports
- This demonstrates why a full port scan is necessary
- The quick scan time (2.57 seconds) indicates the target is responsive

### Redis INFO Command Output (Excerpt)
```
# Server
redis_version:5.0.7
redis_mode:standalone
os:Linux 5.4.0-77-generic x86_64
tcp_port:6379
executable:/usr/bin/redis-server
config_file:/etc/redis/redis.conf

# Memory
used_memory_human:839.48K
total_system_memory_human:1.94G
used_memory_lua_human:41.00K
maxmemory:0
maxmemory_policy:noeviction

# Persistence
aof_enabled:0

# Replication
role:master
connected_slaves:0
```

**Key observations:**
- Redis version 5.0.7 may have known vulnerabilities
- The server is running in standalone mode (not clustered)
- No authentication appears to be required
- System paths are disclosed, potentially useful for further exploitation
- No memory limits are set, which could be exploited for DoS attacks
- Append-only file logging is disabled, making it easier to hide activities
- This is a master node with no slaves, meaning it likely has write access

### Database Enumeration Output
```
127.0.0.1:6379> SELECT 0
OK
127.0.0.1:6379> DBSIZE
(integer) 4
127.0.0.1:6379> KEYS *
1) "temp"
2) "flag"
3) "numb"
4) "stor"
127.0.0.1:6379> GET flag
"HTB{redis_server_compromised}"
```

**Key observations:**
- Database 0 contains 4 keys
- One key is explicitly named "flag", indicating it likely contains our target
- The GET command confirms this by retrieving the flag value
- The other keys (temp, numb, stor) could contain additional information
- No authentication was required to access this sensitive data

## Summary

This CTF challenge provided hands-on experience with Redis database enumeration and exploitation. The most valuable lessons from this exercise include:

1. The importance of thorough port scanning beyond default ranges
2. Understanding Redis as an in-memory database and its security implications
3. Using redis-cli to interact with and enumerate Redis servers
4. The critical security risk of running Redis without authentication

These skills are directly applicable to real-world scenarios such as security assessments of web applications, database security audits, and identifying misconfigurations in production environments.

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
