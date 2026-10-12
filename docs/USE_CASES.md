# 100 practical Redfish use cases

Ten areas, with a plain-language explanation and a Python sample for every case. This curated catalog prioritizes useful hardware workflows; ordering is for navigation. Each case names its required capabilities.

## Run a downloaded sample

Install this repository first: `python -m pip install -e .`. Use Python 3.11 or 3.12.
These samples use the included `RecipeClient`, whose source is in `redfish_lab/recipe_client.py`.

Set `BMC_URL=https://your-bmc`, `BMC_USERNAME` and `BMC_PASSWORD`. The URL is the controller origin,
without a resource path. Keep credentials out of source files. An organization CA can be supplied with
`BMC_CA_BUNDLE=/path/to/ca.pem`. TLS verification stays enabled. The client uses HTTP Basic authentication;
controllers requiring session-only authentication need a different authentication adapter.

If several resources exist, set the relevant ID variable (`BMC_SYSTEM_ID`, `BMC_CHASSIS_ID`,
`BMC_MANAGER_ID`, `STORAGE_ID`, `DRIVE_ID`, etc.). The helper lists available IDs rather than choosing
an arbitrary device. Recipe-specific inputs appear as `required('VARIABLE_NAME')` in the code.

Run `python 095_export-temperature-into-an-otel-dashboard.py` (use your downloaded filename).
All POST/PATCH/DELETE operations print a redacted **dry-run preview** by default.
An operator can explicitly enable execution with `ALLOW_REDFISH_WRITES=1` after reviewing the selected
device, payload and maintenance impact. HTTP 202 means accepted; follow the returned task/monitor and
Retry-After. A preview does not validate hardware compatibility or server-side permissions.

The catalog displays code; it never executes it against a real BMC. **Inspect simulator resource**
performs only a local GET. A simulator example illustrates a related resource and can omit fields or
actions required by the real-hardware recipe. The lab implements a small teaching subset of Redfish.

OTel examples export through the real Python SDK: console by default, or OTLP HTTP/protobuf when
`OTEL_EXPORTER_OTLP_ENDPOINT` is set to a Collector origin, such as `http://127.0.0.1:4318`.
`redfish.*` metric names here are example names, not standardized semantic conventions. Observable gauges
represent current collection/export time; source timestamps are retained separately for inspection.
Continuous adapters need suitable polling intervals, retries, sample freshness checks and log deduplication.
Hardware and application signals correlate by verified server identity and time, not invented trace IDs.

Availability depends on the advertised schema, writable properties, actions, licenses and firmware.
The examples are learning starting points; validate them against the device's supported schema and
vendor documentation. Optional facility/fabric cases require a Redfish-capable PDU, cooling or fabric controller.


## Browse the catalog

| # | Use case | Area | Operation |
| --- | --- | --- | --- |
| 001 | [Discover a BMC and its capabilities](#case-001) | Discovery & inventory | Read |
| 002 | [Populate a hardware asset register](#case-002) | Discovery & inventory | Read |
| 003 | [Plan CPU capacity before deployment](#case-003) | Discovery & inventory | Read |
| 004 | [Find empty or mismatched memory slots](#case-004) | Discovery & inventory | Read |
| 005 | [Inventory GPUs and PCIe accelerators](#case-005) | Discovery & inventory | Read |
| 006 | [Audit physical network adapters](#case-006) | Discovery & inventory | Read |
| 007 | [Inventory physical disks before installation](#case-007) | Discovery & inventory | Read |
| 008 | [Build a firmware inventory](#case-008) | Discovery & inventory | Read |
| 009 | [Map hosts to management controllers](#case-009) | Discovery & inventory | Read |
| 010 | [Locate equipment within a rack](#case-010) | Discovery & inventory | Read |
| 011 | [Screen servers for hardware health issues](#case-011) | Health & diagnostics | Read |
| 012 | [Detect overheating before a shutdown](#case-012) | Health & diagnostics | Read |
| 013 | [Identify stopped or degraded cooling fans](#case-013) | Health & diagnostics | Read |
| 014 | [Check power-supply redundancy](#case-014) | Health & diagnostics | Read |
| 015 | [Pinpoint an unhealthy DIMM](#case-015) | Health & diagnostics | Read |
| 016 | [Spot drives predicted to fail](#case-016) | Health & diagnostics | Read |
| 017 | [Investigate processor throttling](#case-017) | Health & diagnostics | Read |
| 018 | [Detect a downgraded PCIe link](#case-018) | Health & diagnostics | Read |
| 019 | [Triage hardware faults from event history](#case-019) | Health & diagnostics | Read |
| 020 | [Detect a chassis intrusion](#case-020) | Health & diagnostics | Read |
| 021 | [Start a powered-off server](#case-021) | Power & energy | Change |
| 022 | [Shut down gracefully for maintenance](#case-022) | Power & energy | Change |
| 023 | [Power off an unresponsive host](#case-023) | Power & energy | Change |
| 024 | [Restart after a configuration change](#case-024) | Power & energy | Change |
| 025 | [Restore the desired state after a power outage](#case-025) | Power & energy | Change |
| 026 | [Cap a server’s power budget](#case-026) | Power & energy | Change |
| 027 | [Measure instantaneous server power](#case-027) | Power & energy | Read |
| 028 | [Track cumulative energy use](#case-028) | Power & energy | Read |
| 029 | [Assess power-supply conversion efficiency](#case-029) | Power & energy | Read |
| 030 | [Choose a hardware power/performance policy](#case-030) | Power & energy | Change |
| 031 | [Provision a server through one-time PXE boot](#case-031) | Boot & BIOS provisioning | Change |
| 032 | [Boot an installer over UEFI HTTP](#case-032) | Boot & BIOS provisioning | Change |
| 033 | [Boot from an attached installer ISO](#case-033) | Boot & BIOS provisioning | Change |
| 034 | [Explain the server’s available boot options](#case-034) | Boot & BIOS provisioning | Read |
| 035 | [Standardize the persistent boot order](#case-035) | Boot & BIOS provisioning | Change |
| 036 | [Audit BIOS settings for configuration drift](#case-036) | Boot & BIOS provisioning | Read |
| 037 | [Stage model-specific BIOS settings](#case-037) | Boot & BIOS provisioning | Change |
| 038 | [Reset BIOS configuration to defaults](#case-038) | Boot & BIOS provisioning | Change |
| 039 | [Attach virtual installation or rescue media](#case-039) | Boot & BIOS provisioning | Change |
| 040 | [Eject installation media after provisioning](#case-040) | Boot & BIOS provisioning | Change |
| 041 | [Check firmware against an approved baseline](#case-041) | Firmware & maintenance | Read |
| 042 | [Update firmware through a standard action](#case-042) | Firmware & maintenance | Change |
| 043 | [Track an asynchronous maintenance task](#case-043) | Firmware & maintenance | Read |
| 044 | [Restart an unhealthy BMC](#case-044) | Firmware & maintenance | Change |
| 045 | [Light the correct chassis identification LED](#case-045) | Firmware & maintenance | Change |
| 046 | [Check whether staged settings have applied](#case-046) | Firmware & maintenance | Read |
| 047 | [Find firmware targets that can be updated](#case-047) | Firmware & maintenance | Read |
| 048 | [Stage firmware for a later maintenance window](#case-048) | Firmware & maintenance | Change |
| 049 | [Verify the BMC clock before correlating events](#case-049) | Firmware & maintenance | Read |
| 050 | [Request a diagnostic support bundle](#case-050) | Firmware & maintenance | Change |
| 051 | [Map storage controllers to their drives](#case-051) | Storage & data | Read |
| 052 | [Audit logical volumes and RAID levels](#case-052) | Storage & data | Read |
| 053 | [Plan physical storage capacity](#case-053) | Storage & data | Read |
| 054 | [Create a mirrored RAID volume](#case-054) | Storage & data | Change |
| 055 | [Initialize a newly provisioned volume](#case-055) | Storage & data | Change |
| 056 | [Follow a storage rebuild or background operation](#case-056) | Storage & data | Read |
| 057 | [Monitor SSD wear and NVMe error counters](#case-057) | Storage & data | Read |
| 058 | [Identify the physical disk to replace](#case-058) | Storage & data | Change |
| 059 | [Designate a global hot spare](#case-059) | Storage & data | Change |
| 060 | [Sanitize a drive before reuse](#case-060) | Storage & data | Change |
| 061 | [Audit management-network addresses](#case-061) | Networks & fabrics | Read |
| 062 | [Inventory host-network identity for provisioning](#case-062) | Networks & fabrics | Read |
| 063 | [Set a static BMC IPv4 address](#case-063) | Networks & fabrics | Change |
| 064 | [Configure BMC DNS resolvers](#case-064) | Networks & fabrics | Change |
| 065 | [Inspect NIC physical link health](#case-065) | Networks & fabrics | Read |
| 066 | [Check NIC virtualization capability](#case-066) | Networks & fabrics | Read |
| 067 | [Configure a NIC function’s VLAN](#case-067) | Networks & fabrics | Change |
| 068 | [Audit iSCSI boot configuration](#case-068) | Networks & fabrics | Read |
| 069 | [Map managed fabric switches and endpoints](#case-069) | Networks & fabrics | Read |
| 070 | [Configure the BMC’s time servers](#case-070) | Networks & fabrics | Change |
| 071 | [Audit local management accounts](#case-071) | Security & access | Read |
| 072 | [Create a dedicated read-only observer account](#case-072) | Security & access | Change |
| 073 | [Disable a departed user’s BMC account](#case-073) | Security & access | Change |
| 074 | [Rotate a local management password](#case-074) | Security & access | Change |
| 075 | [Review the privileges behind each role](#case-075) | Security & access | Read |
| 076 | [Standardize account lockout behavior](#case-076) | Security & access | Change |
| 077 | [Audit UEFI Secure Boot state](#case-077) | Security & access | Read |
| 078 | [Enable Secure Boot for a prepared platform](#case-078) | Security & access | Change |
| 079 | [Find expiring BMC HTTPS certificates](#case-079) | Security & access | Read |
| 080 | [Replace a management HTTPS certificate](#case-080) | Security & access | Change |
| 081 | [Assign an asset tag during fleet enrollment](#case-081) | Facilities & fleet | Change |
| 082 | [Inventory Redfish-capable rack PDUs](#case-082) | Facilities & fleet | Read |
| 083 | [Measure power at individual rack outlets](#case-083) | Facilities & fleet | Read |
| 084 | [Find overloaded PDU branches](#case-084) | Facilities & fleet | Read |
| 085 | [Power-cycle a selected PDU outlet remotely](#case-085) | Facilities & fleet | Change |
| 086 | [Inventory liquid-cooling distribution units](#case-086) | Facilities & fleet | Read |
| 087 | [Monitor coolant flow and heat removal](#case-087) | Facilities & fleet | Read |
| 088 | [Detect a leak in a liquid-cooled chassis](#case-088) | Facilities & fleet | Read |
| 089 | [Watch rack intake temperature and humidity](#case-089) | Facilities & fleet | Read |
| 090 | [Find field-replaceable assembly part numbers](#case-090) | Facilities & fleet | Read |
| 091 | [Subscribe a hardware-event webhook](#case-091) | Events & OpenTelemetry | Change |
| 092 | [Export hardware fault history as OTel logs](#case-092) | Events & OpenTelemetry | OpenTelemetry |
| 093 | [Discover periodic hardware telemetry reports](#case-093) | Events & OpenTelemetry | Read |
| 094 | [Convert a MetricReport to OTel gauges](#case-094) | Events & OpenTelemetry | OpenTelemetry |
| 095 | [Export temperature into an OTel dashboard](#case-095) | Events & OpenTelemetry | OpenTelemetry |
| 096 | [Export physical power into OTel metrics](#case-096) | Events & OpenTelemetry | OpenTelemetry |
| 097 | [Give hardware and application signals a shared identity](#case-097) | Events & OpenTelemetry | OpenTelemetry |
| 098 | [Trace the latency of a hardware polling request](#case-098) | Events & OpenTelemetry | OpenTelemetry |
| 099 | [Alert when hardware telemetry is stale](#case-099) | Events & OpenTelemetry | OpenTelemetry |
| 100 | [Correlate hardware heat with application request latency](#case-100) | Events & OpenTelemetry | OpenTelemetry |

## Discovery & inventory

<a id="case-001"></a>

### 001 · Discover a BMC and its capabilities

**Why Redfish fits:** A single standard entry point reveals the management features available on an unfamiliar server.

**What you get:** Print the Redfish version and advertised service links before building automation.

**Requires:** A Redfish service root; optional services vary by controller.

**Operation:** Read. [DMTF ServiceRoot schema](https://redfish.dmtf.org/schemas/v1/ServiceRoot.json).

```python
"""001 · Discover a BMC and its capabilities
Requires: A Redfish service root; optional services vary by controller.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    root = rf.root
    show(fields(root, 'RedfishVersion', 'UUID', 'Vendor', 'Product'))
    show({key: value for key, value in root.items()
          if isinstance(value, dict) and '@odata.id' in value})
```

<a id="case-002"></a>

### 002 · Populate a hardware asset register

**Why Redfish fits:** The BMC exposes model and serial identity even before an operating system is installed.

**What you get:** Produce a CMDB-ready record with manufacturer, model, serial number and system UUID.

**Requires:** ComputerSystem inventory; choose BMC_SYSTEM_ID when several systems exist.

**Operation:** Read. [DMTF ComputerSystem schema](https://redfish.dmtf.org/schemas/v1/ComputerSystem.json).

```python
"""002 · Populate a hardware asset register
Requires: ComputerSystem inventory; choose BMC_SYSTEM_ID when several systems exist.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    system = rf.system()
    show(fields(system, 'Id', 'Manufacturer', 'Model', 'SerialNumber',
                'UUID', 'AssetTag', 'HostName', 'BiosVersion'))
```

<a id="case-003"></a>

### 003 · Plan CPU capacity before deployment

**Why Redfish fits:** Processor inventory gives a consistent hardware view without installing an agent on every host.

**What you get:** List sockets, processor models, core counts and threads for placement planning.

**Requires:** The system must advertise a Processors collection.

**Operation:** Read. [DMTF Processor schema](https://redfish.dmtf.org/schemas/v1/Processor.json).

```python
"""003 · Plan CPU capacity before deployment
Requires: The system must advertise a Processors collection.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    processors = rf.members(rf.follow(rf.system(), 'Processors'))
    show([fields(p, 'Socket', 'Model', 'ProcessorType', 'TotalCores',
                 'TotalThreads', 'MaxSpeedMHz') for p in processors])
```

<a id="case-004"></a>

### 004 · Find empty or mismatched memory slots

**Why Redfish fits:** Memory resources describe the physical DIMMs, which an OS capacity total cannot explain.

**What you get:** List DIMM locations, capacities, part numbers and operating speeds.

**Requires:** A Memory collection with populated DIMM inventory.

**Operation:** Read. [DMTF Memory schema](https://redfish.dmtf.org/schemas/v1/Memory.json).

```python
"""004 · Find empty or mismatched memory slots
Requires: A Memory collection with populated DIMM inventory.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    dimms = rf.members(rf.follow(rf.system(), 'Memory'))
    show([fields(d, 'DeviceLocator', 'CapacityMiB', 'PartNumber',
                 'MemoryDeviceType', 'OperatingSpeedMhz', 'Status') for d in dimms])
```

<a id="case-005"></a>

### 005 · Inventory GPUs and PCIe accelerators

**Why Redfish fits:** Chassis PCIe inventory identifies physical add-in devices independently of their host drivers.

**What you get:** List card models, serial numbers, firmware and interface details for accelerator fleets.

**Requires:** Chassis PCIeDevices; GPU detail may need Processor or vendor extensions.

**Operation:** Read. [DMTF PCIeDevice schema](https://redfish.dmtf.org/schemas/v1/PCIeDevice.json).

```python
"""005 · Inventory GPUs and PCIe accelerators
Requires: Chassis PCIeDevices; GPU detail may need Processor or vendor extensions.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    devices = rf.members(rf.follow(rf.chassis(), 'PCIeDevices'))
    show([fields(d, 'Id', 'Manufacturer', 'Model', 'SerialNumber',
                 'FirmwareVersion', 'PCIeInterface') for d in devices])
```

<a id="case-006"></a>

### 006 · Audit physical network adapters

**Why Redfish fits:** A hardware inventory can distinguish installed NIC models from the interfaces currently visible to an OS.

**What you get:** Export NIC model, serial number and controller details for compatibility checks.

**Requires:** Chassis NetworkAdapters collection.

**Operation:** Read. [DMTF NetworkAdapter schema](https://redfish.dmtf.org/schemas/v1/NetworkAdapter.json).

```python
"""006 · Audit physical network adapters
Requires: Chassis NetworkAdapters collection.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    adapters = rf.members(rf.follow(rf.chassis(), 'NetworkAdapters'))
    show([fields(a, 'Id', 'Model', 'Manufacturer', 'SerialNumber',
                 'Controllers', 'Status') for a in adapters])
```

<a id="case-007"></a>

### 007 · Inventory physical disks before installation

**Why Redfish fits:** Storage links reveal the actual drives available to a bare-metal provisioning workflow.

**What you get:** List drive serial numbers, media types, protocols and capacities across controllers.

**Requires:** System Storage with advertised Drives links.

**Operation:** Read. [DMTF Drive schema](https://redfish.dmtf.org/schemas/v1/Drive.json).

```python
"""007 · Inventory physical disks before installation
Requires: System Storage with advertised Drives links.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    records = []
    for storage in rf.members(rf.follow(rf.system(), 'Storage')):
        for link in storage.get('Drives', []):
            records.append(fields(rf.get(link), 'Id', 'SerialNumber',
                                  'MediaType', 'Protocol', 'CapacityBytes', 'Model'))
    show(records)
```

<a id="case-008"></a>

### 008 · Build a firmware inventory

**Why Redfish fits:** UpdateService collects firmware identities in one place instead of requiring separate tools per component.

**What you get:** List installed firmware versions and whether each component is updateable.

**Requires:** UpdateService FirmwareInventory.

**Operation:** Read. [DMTF SoftwareInventory schema](https://redfish.dmtf.org/schemas/v1/SoftwareInventory.json).

```python
"""008 · Build a firmware inventory
Requires: UpdateService FirmwareInventory.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    updates = rf.follow(rf.root, 'UpdateService')
    items = rf.members(rf.follow(updates, 'FirmwareInventory'))
    show([fields(i, 'Id', 'Name', 'Version', 'SoftwareId', 'Updateable') for i in items])
```

<a id="case-009"></a>

### 009 · Map hosts to management controllers

**Why Redfish fits:** Standard topology links connect a server to the controller that manages it, avoiding guessed host-to-BMC mappings.

**What you get:** Print each system identity and its advertised ManagedBy relationships.

**Requires:** ComputerSystem Links.ManagedBy populated by the service.

**Operation:** Read. [DMTF ComputerSystem schema](https://redfish.dmtf.org/schemas/v1/ComputerSystem.json).

```python
"""009 · Map hosts to management controllers
Requires: ComputerSystem Links.ManagedBy populated by the service.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for system in rf.members(rf.follow(rf.root, 'Systems')):
        show({'system': fields(system, 'Id', 'UUID', 'SerialNumber'),
              'managed_by': system.get('Links', {}).get('ManagedBy', [])})
```

<a id="case-010"></a>

### 010 · Locate equipment within a rack

**Why Redfish fits:** Chassis location metadata helps technicians connect a software incident to the physical machine.

**What you get:** Read chassis type, asset tag and available rack/placement information.

**Requires:** Chassis Location metadata; operators may need to populate it first.

**Operation:** Read. [DMTF Chassis schema](https://redfish.dmtf.org/schemas/v1/Chassis.json).

```python
"""010 · Locate equipment within a rack
Requires: Chassis Location metadata; operators may need to populate it first.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for chassis in rf.members(rf.follow(rf.root, 'Chassis')):
        show(fields(chassis, 'Id', 'ChassisType', 'AssetTag', 'Location', 'SerialNumber'))
```

## Health & diagnostics

<a id="case-011"></a>

### 011 · Screen servers for hardware health issues

**Why Redfish fits:** An out-of-band health rollup is useful when the host is down or its monitoring agent is unreachable.

**What you get:** Print per-system health rollups and identify non-OK or unavailable status.

**Requires:** ComputerSystem Status.HealthRollup or Status.Health.

**Operation:** Read. [DMTF ComputerSystem schema](https://redfish.dmtf.org/schemas/v1/ComputerSystem.json).

```python
"""011 · Screen servers for hardware health issues
Requires: ComputerSystem Status.HealthRollup or Status.Health.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for system in rf.members(rf.follow(rf.root, 'Systems')):
        status = system.get('Status', {})
        health = status.get('HealthRollup') or status.get('Health')
        show({'system': system.get('Id'), 'health': health,
              'needs_review': health != 'OK', 'status': status})
```

<a id="case-012"></a>

### 012 · Detect overheating before a shutdown

**Why Redfish fits:** BMC temperature sensors keep working independently of application monitoring.

**What you get:** Compare valid Celsius readings with each sensor’s advertised upper critical threshold.

**Requires:** Modern Sensors with Temperature readings in Cel; legacy devices may expose Thermal instead.

**Operation:** Read. [DMTF Sensor schema](https://redfish.dmtf.org/schemas/v1/Sensor.json).

```python
"""012 · Detect overheating before a shutdown
Requires: Modern Sensors with Temperature readings in Cel; legacy devices may expose Thermal instead.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for sensor in rf.sensors('Temperature'):
        reading = sensor.get('Reading')
        critical = sensor.get('Thresholds', {}).get('UpperCritical', {}).get('Reading')
        if sensor.get('ReadingUnits') == 'Cel' and isinstance(reading, (int, float)):
            show({'sensor': sensor.get('Name'), 'celsius': reading,
                  'critical_threshold': critical,
                  'over_threshold': reading >= critical if isinstance(critical, (int, float)) else None})
```

<a id="case-013"></a>

### 013 · Identify stopped or degraded cooling fans

**Why Redfish fits:** Hardware fan readings expose cooling failures even when the operating system has no fan driver.

**What you get:** List rotational readings with their units and status; a zero reading needs context because some fans intentionally stop.

**Requires:** Rotational Sensors with Reading, ReadingUnits and Status.

**Operation:** Read. [DMTF Sensor schema](https://redfish.dmtf.org/schemas/v1/Sensor.json).

```python
"""013 · Identify stopped or degraded cooling fans
Requires: Rotational Sensors with Reading, ReadingUnits and Status.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for sensor in rf.sensors('Rotational'):
        show(fields(sensor, 'Id', 'Name', 'Reading', 'ReadingUnits',
                    'PhysicalContext', 'Status'))
```

<a id="case-014"></a>

### 014 · Check power-supply redundancy

**Why Redfish fits:** The chassis power subsystem reveals lost redundancy before the remaining supply fails.

**What you get:** Read redundancy groups and the health of each advertised power supply.

**Requires:** Modern PowerSubsystem with PowerSupplies and PowerSupplyRedundancy.

**Operation:** Read. [DMTF PowerSubsystem schema](https://redfish.dmtf.org/schemas/v1/PowerSubsystem.json).

```python
"""014 · Check power-supply redundancy
Requires: Modern PowerSubsystem with PowerSupplies and PowerSupplyRedundancy.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    power = rf.follow(rf.chassis(), 'PowerSubsystem')
    show({'redundancy': power.get('PowerSupplyRedundancy')})
    show([fields(p, 'Id', 'Model', 'LineInputStatus', 'Status')
          for p in rf.members(rf.follow(power, 'PowerSupplies'))])
```

<a id="case-015"></a>

### 015 · Pinpoint an unhealthy DIMM

**Why Redfish fits:** A per-DIMM health record identifies the physical slot to replace instead of reporting only a generic memory error.

**What you get:** Print DIMM status alongside its locator and serial number.

**Requires:** Memory collection and per-module Status; detailed error counts require Metrics support.

**Operation:** Read. [DMTF Memory schema](https://redfish.dmtf.org/schemas/v1/Memory.json).

```python
"""015 · Pinpoint an unhealthy DIMM
Requires: Memory collection and per-module Status; detailed error counts require Metrics support.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for dimm in rf.members(rf.follow(rf.system(), 'Memory')):
        show(fields(dimm, 'Id', 'DeviceLocator', 'SerialNumber', 'Status'))
```

<a id="case-016"></a>

### 016 · Spot drives predicted to fail

**Why Redfish fits:** The BMC can expose controller-reported drive health before a drive disappears from the host.

**What you get:** List failure prediction and remaining media life; missing values remain unknown.

**Requires:** Drive.FailurePredicted and optionally PredictedMediaLifeLeftPercent.

**Operation:** Read. [DMTF Drive schema](https://redfish.dmtf.org/schemas/v1/Drive.json).

```python
"""016 · Spot drives predicted to fail
Requires: Drive.FailurePredicted and optionally PredictedMediaLifeLeftPercent.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for storage in rf.members(rf.follow(rf.system(), 'Storage')):
        for link in storage.get('Drives', []):
            show(fields(rf.get(link), 'Id', 'SerialNumber', 'FailurePredicted',
                        'PredictedMediaLifeLeftPercent', 'Status'))
```

<a id="case-017"></a>

### 017 · Investigate processor throttling

**Why Redfish fits:** Hardware throttle causes help explain slower work that ordinary CPU utilization alone cannot.

**What you get:** Read operating speed, throttle state and reported causes for each processor.

**Requires:** Recent Processor schema with Throttled and ThrottleCauses; these fields are optional.

**Operation:** Read. [DMTF Processor schema](https://redfish.dmtf.org/schemas/v1/Processor.json).

```python
"""017 · Investigate processor throttling
Requires: Recent Processor schema with Throttled and ThrottleCauses; these fields are optional.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for processor in rf.members(rf.follow(rf.system(), 'Processors')):
        show(fields(processor, 'Id', 'OperatingSpeedMHz', 'Throttled',
                    'ThrottleCauses', 'TDPWatts'))
```

<a id="case-018"></a>

### 018 · Detect a downgraded PCIe link

**Why Redfish fits:** PCIe link metadata can reveal a card running below its expected lane width or generation.

**What you get:** Show current and maximum PCIe interface details for comparison with the hardware design.

**Requires:** PCIeDevice.PCIeInterface populated by the BMC.

**Operation:** Read. [DMTF PCIeDevice schema](https://redfish.dmtf.org/schemas/v1/PCIeDevice.json).

```python
"""018 · Detect a downgraded PCIe link
Requires: PCIeDevice.PCIeInterface populated by the BMC.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for card in rf.members(rf.follow(rf.chassis(), 'PCIeDevices')):
        show({'card': card.get('Id'), 'model': card.get('Model'),
              'pcie_interface': card.get('PCIeInterface'), 'status': card.get('Status')})
```

<a id="case-019"></a>

### 019 · Triage hardware faults from event history

**Why Redfish fits:** Persistent BMC logs preserve hardware faults across host crashes and OS reinstallations.

**What you get:** Read log entries with severity, creation time and message identifiers.

**Requires:** Manager LogServices with Entries; logs may also be linked from Systems or Chassis.

**Operation:** Read. [DMTF LogEntry schema](https://redfish.dmtf.org/schemas/v1/LogEntry.json).

```python
"""019 · Triage hardware faults from event history
Requires: Manager LogServices with Entries; logs may also be linked from Systems or Chassis.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for log in rf.members(rf.follow(rf.manager(), 'LogServices')):
        for entry in rf.members(rf.follow(log, 'Entries')):
            show(fields(entry, 'Id', 'Created', 'Severity', 'MessageId', 'Message'))
```

<a id="case-020"></a>

### 020 · Detect a chassis intrusion

**Why Redfish fits:** A chassis-open sensor provides a physical security signal beyond software authentication logs.

**What you get:** Print the advertised intrusion sensor state and its rearm policy.

**Requires:** Chassis.PhysicalSecurity; a physical intrusion sensor must be installed.

**Operation:** Read. [DMTF Chassis schema](https://redfish.dmtf.org/schemas/v1/Chassis.json).

```python
"""020 · Detect a chassis intrusion
Requires: Chassis.PhysicalSecurity; a physical intrusion sensor must be installed.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    show({'chassis': rf.chassis().get('Id'),
          'physical_security': rf.chassis().get('PhysicalSecurity')})
```

## Power & energy

<a id="case-021"></a>

### 021 · Start a powered-off server

**Why Redfish fits:** The BMC remains reachable when the main host is off, making remote startup possible.

**What you get:** Request host power-on and then re-read PowerState.

**Requires:** ComputerSystem.Reset must advertise the requested ResetType; execution needs power privileges.

**Operation:** Change. [DMTF ComputerSystem schema](https://redfish.dmtf.org/schemas/v1/ComputerSystem.json).

```python
"""021 · Start a powered-off server
Requires: ComputerSystem.Reset must advertise the requested ResetType; execution needs power privileges.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    system = rf.system()
    show(rf.action(system, 'ComputerSystem.Reset', {'ResetType': 'On'}))
    # Re-read after an appropriate wait when executing on real hardware.
    show(fields(rf.get(system), 'PowerState', 'BootProgress', 'LastResetTime'))
```

<a id="case-022"></a>

### 022 · Shut down gracefully for maintenance

**Why Redfish fits:** A standard reset action lets an automation request an orderly host shutdown.

**What you get:** Ask the host to shut down; acceptance does not guarantee the OS has finished.

**Requires:** ComputerSystem.Reset must advertise the requested ResetType; execution needs power privileges.

**Operation:** Change. [DMTF ComputerSystem schema](https://redfish.dmtf.org/schemas/v1/ComputerSystem.json).

```python
"""022 · Shut down gracefully for maintenance
Requires: ComputerSystem.Reset must advertise the requested ResetType; execution needs power privileges.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    system = rf.system()
    show(rf.action(system, 'ComputerSystem.Reset', {'ResetType': 'GracefulShutdown'}))
    # Re-read after an appropriate wait when executing on real hardware.
    show(fields(rf.get(system), 'PowerState', 'BootProgress', 'LastResetTime'))
```

<a id="case-023"></a>

### 023 · Power off an unresponsive host

**Why Redfish fits:** The independent management path can recover a server whose OS no longer responds.

**What you get:** Request a forced power-off; this interrupts workloads and can lose unsaved data.

**Requires:** ComputerSystem.Reset must advertise the requested ResetType; execution needs power privileges.

**Operation:** Change. [DMTF ComputerSystem schema](https://redfish.dmtf.org/schemas/v1/ComputerSystem.json).

```python
"""023 · Power off an unresponsive host
Requires: ComputerSystem.Reset must advertise the requested ResetType; execution needs power privileges.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    system = rf.system()
    show(rf.action(system, 'ComputerSystem.Reset', {'ResetType': 'ForceOff'}))
    # Re-read after an appropriate wait when executing on real hardware.
    show(fields(rf.get(system), 'PowerState', 'BootProgress', 'LastResetTime'))
```

<a id="case-024"></a>

### 024 · Restart after a configuration change

**Why Redfish fits:** A discovered reset action makes reboot orchestration consistent across supported servers.

**What you get:** Request a graceful restart and follow subsequent power/boot progress.

**Requires:** ComputerSystem.Reset must advertise the requested ResetType; execution needs power privileges.

**Operation:** Change. [DMTF ComputerSystem schema](https://redfish.dmtf.org/schemas/v1/ComputerSystem.json).

```python
"""024 · Restart after a configuration change
Requires: ComputerSystem.Reset must advertise the requested ResetType; execution needs power privileges.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    system = rf.system()
    show(rf.action(system, 'ComputerSystem.Reset', {'ResetType': 'GracefulRestart'}))
    # Re-read after an appropriate wait when executing on real hardware.
    show(fields(rf.get(system), 'PowerState', 'BootProgress', 'LastResetTime'))
```

<a id="case-025"></a>

### 025 · Restore the desired state after a power outage

**Why Redfish fits:** PowerRestorePolicy lets a bare-metal fleet express how hosts should behave when AC power returns.

**What you get:** Preview a policy change to restore the host’s last power state.

**Requires:** Writable ComputerSystem.PowerRestorePolicy and support for LastState.

**Operation:** Change. [DMTF ComputerSystem schema](https://redfish.dmtf.org/schemas/v1/ComputerSystem.json).

```python
"""025 · Restore the desired state after a power outage
Requires: Writable ComputerSystem.PowerRestorePolicy and support for LastState.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    system = rf.system()
    show({'current_policy': system.get('PowerRestorePolicy')})
    show(rf.patch(system, {'PowerRestorePolicy': 'LastState'}))
```

<a id="case-026"></a>

### 026 · Cap a server’s power budget

**Why Redfish fits:** Hardware power controls can enforce a rack budget without relying on each application to cooperate.

**What you get:** Preview a modern power-limit set point in watts, respecting advertised bounds.

**Requires:** Writable EnvironmentMetrics.PowerLimitWatts excerpt; older services may use legacy PowerControl.

**Operation:** Change. [DMTF EnvironmentMetrics schema](https://redfish.dmtf.org/schemas/v1/EnvironmentMetrics.json).

```python
"""026 · Cap a server’s power budget
Requires: Writable EnvironmentMetrics.PowerLimitWatts excerpt; older services may use legacy PowerControl.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    environment = rf.follow(rf.chassis(), 'EnvironmentMetrics')
    control = environment.get('PowerLimitWatts')
    if not isinstance(control, dict):
        raise CapabilityError('No modern power limit is advertised')
    watts = float(required('POWER_CAP_WATTS'))
    if control.get('AllowableMin') is not None and watts < control['AllowableMin']:
        raise ValueError('Requested cap is below the hardware minimum')
    if control.get('AllowableMax') is not None and watts > control['AllowableMax']:
        raise ValueError('Requested cap exceeds the hardware maximum')
    show(rf.patch(environment, {'PowerLimitWatts': {'SetPoint': watts}}))
```

<a id="case-027"></a>

### 027 · Measure instantaneous server power

**Why Redfish fits:** BMC power sensors measure the physical system rather than estimating consumption from CPU utilization.

**What you get:** Read power sensors with units, timestamps and physical context.

**Requires:** Sensors with ReadingType Power; only compare measurements with compatible units.

**Operation:** Read. [DMTF Sensor schema](https://redfish.dmtf.org/schemas/v1/Sensor.json).

```python
"""027 · Measure instantaneous server power
Requires: Sensors with ReadingType Power; only compare measurements with compatible units.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for sensor in rf.sensors('Power'):
        show(fields(sensor, 'Id', 'Reading', 'ReadingUnits', 'ReadingTime', 'PhysicalContext'))
```

<a id="case-028"></a>

### 028 · Track cumulative energy use

**Why Redfish fits:** A hardware energy counter supports consumption reports without installing host software.

**What you get:** Read EnergykWh/EnergyJoules excerpts; use differences over time and handle counter resets.

**Requires:** EnvironmentMetrics energy readings supported by the equipment.

**Operation:** Read. [DMTF EnvironmentMetrics schema](https://redfish.dmtf.org/schemas/v1/EnvironmentMetrics.json).

```python
"""028 · Track cumulative energy use
Requires: EnvironmentMetrics energy readings supported by the equipment.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    environment = rf.follow(rf.chassis(), 'EnvironmentMetrics')
    show(fields(environment, 'EnergykWh', 'EnergyJoules'))
    # Persist timestamped readings externally; subtract successive values only
    # when the same counter has not reset. Watts and kWh are different quantities.
```

<a id="case-029"></a>

### 029 · Assess power-supply conversion efficiency

**Why Redfish fits:** Input and output power measurements help locate inefficient or overloaded supplies.

**What you get:** Estimate output/input efficiency only when both readings are present and input is positive.

**Requires:** PowerSupply.Metrics with InputPowerWatts and OutputPowerWatts excerpts.

**Operation:** Read. [DMTF PowerSupplyMetrics schema](https://redfish.dmtf.org/schemas/v1/PowerSupplyMetrics.json).

```python
"""029 · Assess power-supply conversion efficiency
Requires: PowerSupply.Metrics with InputPowerWatts and OutputPowerWatts excerpts.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    power = rf.follow(rf.chassis(), 'PowerSubsystem')
    for supply in rf.members(rf.follow(power, 'PowerSupplies')):
        metrics = rf.follow(supply, 'Metrics')
        incoming = (metrics.get('InputPowerWatts') or {}).get('Reading')
        outgoing = (metrics.get('OutputPowerWatts') or {}).get('Reading')
        efficiency = (100 * outgoing / incoming
                      if isinstance(incoming, (int, float)) and incoming > 0
                      and isinstance(outgoing, (int, float)) else None)
        show({'supply': supply.get('Id'), 'estimated_efficiency_percent': efficiency})
```

<a id="case-030"></a>

### 030 · Choose a hardware power/performance policy

**Why Redfish fits:** A platform power mode can align hardware behavior with a fleet’s energy or performance goals.

**What you get:** Preview PowerSaving mode where the system supports that writable policy.

**Requires:** ComputerSystem.PowerMode and platform support for PowerSaving; effects vary by platform.

**Operation:** Change. [DMTF ComputerSystem schema](https://redfish.dmtf.org/schemas/v1/ComputerSystem.json).

```python
"""030 · Choose a hardware power/performance policy
Requires: ComputerSystem.PowerMode and platform support for PowerSaving; effects vary by platform.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    system = rf.system()
    if 'PowerMode' not in system:
        raise CapabilityError('PowerMode is not advertised')
    show({'current_mode': system['PowerMode']})
    show(rf.patch(system, {'PowerMode': 'PowerSaving'}))
```

## Boot & BIOS provisioning

<a id="case-031"></a>

### 031 · Provision a server through one-time PXE boot

**Why Redfish fits:** A one-time boot override starts bare-metal provisioning while preserving the usual disk boot policy.

**What you get:** Preview PXE as the next boot source; provisioning services and a separate restart are still required.

**Requires:** ComputerSystem Boot supports Pxe and Once; a working PXE network is required.

**Operation:** Change. [DMTF ComputerSystem schema](https://redfish.dmtf.org/schemas/v1/ComputerSystem.json).

```python
"""031 · Provision a server through one-time PXE boot
Requires: ComputerSystem Boot supports Pxe and Once; a working PXE network is required.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    show(rf.boot('Pxe'))
    # This selects the next boot; it does not reboot or install an OS by itself.
```

<a id="case-032"></a>

### 032 · Boot an installer over UEFI HTTP

**Why Redfish fits:** Redfish can point compatible firmware at an HTTP boot image for remote provisioning.

**What you get:** Preview a one-time UEFI HTTP boot URI and target.

**Requires:** Boot target UefiHttp and writable HttpBootUri; firmware and network must support HTTP boot.

**Operation:** Change. [DMTF ComputerSystem schema](https://redfish.dmtf.org/schemas/v1/ComputerSystem.json).

```python
"""032 · Boot an installer over UEFI HTTP
Requires: Boot target UefiHttp and writable HttpBootUri; firmware and network must support HTTP boot.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    show(rf.boot('UefiHttp', HttpBootUri=required('BOOT_IMAGE_URI')))
    # Use a trusted boot image and the platform’s supported HTTP/HTTPS configuration.
```

<a id="case-033"></a>

### 033 · Boot from an attached installer ISO

**Why Redfish fits:** A remote CD override makes virtual-media installation possible without a technician inserting a disk.

**What you get:** Preview a one-time CD boot; attach media first and restart separately.

**Requires:** ComputerSystem Boot supports Cd and virtual media is already attached.

**Operation:** Change. [DMTF ComputerSystem schema](https://redfish.dmtf.org/schemas/v1/ComputerSystem.json).

```python
"""033 · Boot from an attached installer ISO
Requires: ComputerSystem Boot supports Cd and virtual media is already attached.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    show(rf.boot('Cd'))
    # Attach the ISO using case 039, then request a restart in a maintenance window.
```

<a id="case-034"></a>

### 034 · Explain the server’s available boot options

**Why Redfish fits:** Standard UEFI boot-option resources reveal which named devices firmware can actually start.

**What you get:** List boot option references, display names and UEFI paths.

**Requires:** ComputerSystem Boot.BootOptions collection.

**Operation:** Read. [DMTF BootOption schema](https://redfish.dmtf.org/schemas/v1/BootOption.json).

```python
"""034 · Explain the server’s available boot options
Requires: ComputerSystem Boot.BootOptions collection.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    boot = rf.system().get('Boot', {})
    options = rf.members(rf.follow(boot, 'BootOptions'))
    show([fields(o, 'BootOptionReference', 'DisplayName', 'UefiDevicePath',
                 'BootOptionEnabled') for o in options])
```

<a id="case-035"></a>

### 035 · Standardize the persistent boot order

**Why Redfish fits:** Firmware boot ordering can be staged consistently across a bare-metal fleet.

**What you get:** Validate a requested list against discovered BootOptionReference values and preview the change.

**Requires:** Writable BootOrder and BootOptions; a reboot may be needed to apply pending settings.

**Operation:** Change. [DMTF ComputerSystem schema](https://redfish.dmtf.org/schemas/v1/ComputerSystem.json).

```python
"""035 · Standardize the persistent boot order
Requires: Writable BootOrder and BootOptions; a reboot may be needed to apply pending settings.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    system = rf.system()
    options = rf.members(rf.follow(system.get('Boot', {}), 'BootOptions'))
    known = {o.get('BootOptionReference') for o in options}
    order = json.loads(required('BOOT_ORDER_JSON'))
    if not isinstance(order, list) or len(order) != len(set(order)) or not set(order) <= known:
        raise ValueError('Use a unique JSON list of advertised boot references')
    target = rf.settings(system) if system.get('@Redfish.Settings') else system
    show(rf.patch(target, {'Boot': {'BootOrder': order}}))
```

<a id="case-036"></a>

### 036 · Audit BIOS settings for configuration drift

**Why Redfish fits:** The BMC exposes firmware attributes before and after an OS installation.

**What you get:** Print current BIOS attributes and the registry name used to interpret their allowed values.

**Requires:** System Bios link; attribute names and values are vendor-specific.

**Operation:** Read. [DMTF Bios schema](https://redfish.dmtf.org/schemas/v1/Bios.json).

```python
"""036 · Audit BIOS settings for configuration drift
Requires: System Bios link; attribute names and values are vendor-specific.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    bios = rf.follow(rf.system(), 'Bios')
    show(fields(bios, 'AttributeRegistry', 'Attributes'))
    # Compare with a versioned baseline for this exact server model/BIOS version.
```

<a id="case-037"></a>

### 037 · Stage model-specific BIOS settings

**Why Redfish fits:** The Settings model separates proposed firmware changes from currently active settings.

**What you get:** Preview a change to the advertised pending BIOS resource; reboot separately to apply it.

**Requires:** Bios @Redfish.Settings; validate desired values with the advertised AttributeRegistry first.

**Operation:** Change. [DMTF Bios schema](https://redfish.dmtf.org/schemas/v1/Bios.json).

```python
"""037 · Stage model-specific BIOS settings
Requires: Bios @Redfish.Settings; validate desired values with the advertised AttributeRegistry first.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    bios = rf.follow(rf.system(), 'Bios')
    desired = json.loads(required('BIOS_ATTRIBUTES_JSON'))
    if not isinstance(desired, dict) or not desired or not set(desired) <= set(bios.get('Attributes', {})):
        raise ValueError('Choose attribute names advertised by this BIOS')
    # AttributeRegistry defines vendor-specific value types and dependencies.
    show(rf.patch(rf.settings(bios), {'Attributes': desired}))
```

<a id="case-038"></a>

### 038 · Reset BIOS configuration to defaults

**Why Redfish fits:** A discovered BIOS reset action supports repeatable recovery from a bad firmware configuration.

**What you get:** Preview the ResetBios action; consult pending-state information and reboot requirements afterward.

**Requires:** Advertised Bios.ResetBios action; defaults can change boot and device settings.

**Operation:** Change. [DMTF Bios schema](https://redfish.dmtf.org/schemas/v1/Bios.json).

```python
"""038 · Reset BIOS configuration to defaults
Requires: Advertised Bios.ResetBios action; defaults can change boot and device settings.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    bios = rf.follow(rf.system(), 'Bios')
    show(rf.action(bios, 'Bios.ResetBios', {}))
    show(fields(rf.get(bios), 'ResetBiosToDefaultsPending', '@Redfish.Settings'))
```

<a id="case-039"></a>

### 039 · Attach virtual installation or rescue media

**Why Redfish fits:** The BMC can present a remote image as a local disk even when the host OS is absent.

**What you get:** Preview an InsertMedia action with a read-only ISO URL.

**Requires:** Manager VirtualMedia with InsertMedia; set MEDIA_ID when more than one slot exists.

**Operation:** Change. [DMTF VirtualMedia schema](https://redfish.dmtf.org/schemas/v1/VirtualMedia.json).

```python
"""039 · Attach virtual installation or rescue media
Requires: Manager VirtualMedia with InsertMedia; set MEDIA_ID when more than one slot exists.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    media = rf.choose(rf.members(rf.follow(rf.manager(), 'VirtualMedia')), 'MEDIA_ID')
    show(rf.action(media, 'VirtualMedia.InsertMedia', {
        'Image': required('ISO_IMAGE_URI'), 'Inserted': True, 'WriteProtected': True,
    }))
```

<a id="case-040"></a>

### 040 · Eject installation media after provisioning

**Why Redfish fits:** Removing virtual media avoids accidentally booting an old installer during a later restart.

**What you get:** Preview EjectMedia on the selected advertised virtual-media slot.

**Requires:** VirtualMedia.EjectMedia action.

**Operation:** Change. [DMTF VirtualMedia schema](https://redfish.dmtf.org/schemas/v1/VirtualMedia.json).

```python
"""040 · Eject installation media after provisioning
Requires: VirtualMedia.EjectMedia action.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    media = rf.choose(rf.members(rf.follow(rf.manager(), 'VirtualMedia')), 'MEDIA_ID')
    show(rf.action(media, 'VirtualMedia.EjectMedia', {}))
```

## Firmware & maintenance

<a id="case-041"></a>

### 041 · Check firmware against an approved baseline

**Why Redfish fits:** One inventory API can feed compliance checks for BMC, BIOS and supported device firmware.

**What you get:** Report version matches, mismatches and components missing from the expected inventory.

**Requires:** FirmwareInventory; FIRMWARE_BASELINE_JSON maps exact inventory IDs to approved versions.

**Operation:** Read. [DMTF SoftwareInventory schema](https://redfish.dmtf.org/schemas/v1/SoftwareInventory.json).

```python
"""041 · Check firmware against an approved baseline
Requires: FirmwareInventory; FIRMWARE_BASELINE_JSON maps exact inventory IDs to approved versions.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    updates = rf.follow(rf.root, 'UpdateService')
    items = {i['Id']: i for i in rf.members(rf.follow(updates, 'FirmwareInventory'))}
    baseline = json.loads(required('FIRMWARE_BASELINE_JSON'))
    for identity, expected in baseline.items():
        actual = items.get(identity, {}).get('Version')
        show({'id': identity, 'expected': expected, 'actual': actual, 'matches': actual == expected})
```

<a id="case-042"></a>

### 042 · Update firmware through a standard action

**Why Redfish fits:** SimpleUpdate gives an advertised management path for installing a supported firmware image.

**What you get:** Preview the firmware request; an executed update may return 202 and a task Location.

**Requires:** UpdateService.SimpleUpdate; image compatibility, privileges and reboot rules are platform-specific.

**Operation:** Change. [DMTF UpdateService schema](https://redfish.dmtf.org/schemas/v1/UpdateService.json).

```python
"""042 · Update firmware through a standard action
Requires: UpdateService.SimpleUpdate; image compatibility, privileges and reboot rules are platform-specific.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    updates = rf.follow(rf.root, 'UpdateService')
    show(rf.action(updates, 'UpdateService.SimpleUpdate', {
        'ImageURI': required('FIRMWARE_IMAGE_URI'),
    }))
    # HTTP 202 means accepted, not finished. Inspect the returned task/monitor.
```

<a id="case-043"></a>

### 043 · Track an asynchronous maintenance task

**Why Redfish fits:** Task resources make long-running work observable instead of treating acceptance as completion.

**What you get:** Print task state, status, percentage and messages from the advertised Tasks service.

**Requires:** ServiceRoot Tasks and a Task collection; select TASK_ID when several tasks exist.

**Operation:** Read. [DMTF Task schema](https://redfish.dmtf.org/schemas/v1/Task.json).

```python
"""043 · Track an asynchronous maintenance task
Requires: ServiceRoot Tasks and a Task collection; select TASK_ID when several tasks exist.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    service = rf.follow(rf.root, 'Tasks')
    task = rf.choose(rf.members(rf.follow(service, 'Tasks')), 'TASK_ID')
    show(fields(task, 'Id', 'TaskState', 'TaskStatus', 'PercentComplete',
                'StartTime', 'EndTime', 'Messages', 'TaskMonitor'))
    # Poll at the server’s suggested Retry-After interval in a production workflow.
```

<a id="case-044"></a>

### 044 · Restart an unhealthy BMC

**Why Redfish fits:** Manager reset can recover the management controller independently from the host’s power action.

**What you get:** Preview a graceful BMC restart; management connectivity will temporarily disappear.

**Requires:** Manager.Reset with GracefulRestart; do not confuse it with ComputerSystem.Reset.

**Operation:** Change. [DMTF Manager schema](https://redfish.dmtf.org/schemas/v1/Manager.json).

```python
"""044 · Restart an unhealthy BMC
Requires: Manager.Reset with GracefulRestart; do not confuse it with ComputerSystem.Reset.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    manager = rf.manager()
    show(rf.action(manager, 'Manager.Reset', {'ResetType': 'GracefulRestart'}))
```

<a id="case-045"></a>

### 045 · Light the correct chassis identification LED

**Why Redfish fits:** A standard locator control helps a remote operator direct a technician to the right server.

**What you get:** Preview LocationIndicatorActive=true on the selected chassis.

**Requires:** Writable Chassis.LocationIndicatorActive; older devices use IndicatorLED.

**Operation:** Change. [DMTF Chassis schema](https://redfish.dmtf.org/schemas/v1/Chassis.json).

```python
"""045 · Light the correct chassis identification LED
Requires: Writable Chassis.LocationIndicatorActive; older devices use IndicatorLED.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    chassis = rf.chassis()
    if 'LocationIndicatorActive' not in chassis:
        raise CapabilityError('Modern locator LED control is not advertised')
    show(rf.patch(chassis, {'LocationIndicatorActive': True}))
```

<a id="case-046"></a>

### 046 · Check whether staged settings have applied

**Why Redfish fits:** The Settings annotation links active configuration to pending configuration and application messages.

**What you get:** Display active/pending BIOS values and Settings messages instead of assuming PATCH changed the running firmware.

**Requires:** Bios @Redfish.Settings.SettingsObject; messages and timestamps depend on the implementation.

**Operation:** Read. [DMTF Bios schema](https://redfish.dmtf.org/schemas/v1/Bios.json).

```python
"""046 · Check whether staged settings have applied
Requires: Bios @Redfish.Settings.SettingsObject; messages and timestamps depend on the implementation.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    bios = rf.follow(rf.system(), 'Bios')
    pending = rf.settings(bios)
    show({'active': bios.get('Attributes'), 'pending': pending.get('Attributes'),
          'application_info': bios.get('@Redfish.Settings')})
```

<a id="case-047"></a>

### 047 · Find firmware targets that can be updated

**Why Redfish fits:** SoftwareInventory marks updateable components and their reset requirements before maintenance begins.

**What you get:** List eligible targets with reset requirements and stable resource links.

**Requires:** FirmwareInventory Updateable and optional ResetRequiredOnUpdate.

**Operation:** Read. [DMTF SoftwareInventory schema](https://redfish.dmtf.org/schemas/v1/SoftwareInventory.json).

```python
"""047 · Find firmware targets that can be updated
Requires: FirmwareInventory Updateable and optional ResetRequiredOnUpdate.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    updates = rf.follow(rf.root, 'UpdateService')
    for item in rf.members(rf.follow(updates, 'FirmwareInventory')):
        if item.get('Updateable') is True:
            show(fields(item, '@odata.id', 'Id', 'Version', 'ResetRequiredOnUpdate'))
```

<a id="case-048"></a>

### 048 · Stage firmware for a later maintenance window

**Why Redfish fits:** Compatible services can receive an image before activation, reducing work during a planned outage.

**What you get:** Preview SimpleUpdate with Stage=true; activation is a separate supported workflow.

**Requires:** A recent SimpleUpdate action supporting Stage; check its ActionInfo or vendor documentation.

**Operation:** Change. [DMTF UpdateService schema](https://redfish.dmtf.org/schemas/v1/UpdateService.json).

```python
"""048 · Stage firmware for a later maintenance window
Requires: A recent SimpleUpdate action supporting Stage; check its ActionInfo or vendor documentation.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    updates = rf.follow(rf.root, 'UpdateService')
    show(rf.action(updates, 'UpdateService.SimpleUpdate', {
        'ImageURI': required('FIRMWARE_IMAGE_URI'), 'Stage': True,
    }))
```

<a id="case-049"></a>

### 049 · Verify the BMC clock before correlating events

**Why Redfish fits:** Controller time determines the meaning of hardware event timestamps in incident timelines.

**What you get:** Read manager time, local offset and configured time source for clock-alignment checks.

**Requires:** Manager time fields; compare with a trusted UTC reference outside this one-shot sample.

**Operation:** Read. [DMTF Manager schema](https://redfish.dmtf.org/schemas/v1/Manager.json).

```python
"""049 · Verify the BMC clock before correlating events
Requires: Manager time fields; compare with a trusted UTC reference outside this one-shot sample.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    show(fields(rf.manager(), 'DateTime', 'DateTimeLocalOffset', 'DateTimeSource', 'TimeZoneName'))
```

<a id="case-050"></a>

### 050 · Request a diagnostic support bundle

**Why Redfish fits:** A discovered diagnostic action can gather controller evidence without needing a functional host OS.

**What you get:** Preview a manager diagnostic collection and inspect its resulting task or log entry when executed.

**Requires:** LogService.CollectDiagnosticData supporting Manager; select LOG_SERVICE_ID.

**Operation:** Change. [DMTF LogService schema](https://redfish.dmtf.org/schemas/v1/LogService.json).

```python
"""050 · Request a diagnostic support bundle
Requires: LogService.CollectDiagnosticData supporting Manager; select LOG_SERVICE_ID.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    log = rf.choose(rf.members(rf.follow(rf.manager(), 'LogServices')), 'LOG_SERVICE_ID')
    show(rf.action(log, 'LogService.CollectDiagnosticData', {'DiagnosticDataType': 'Manager'}))
```

## Storage & data

<a id="case-051"></a>

### 051 · Map storage controllers to their drives

**Why Redfish fits:** Controller and drive relationships explain the physical topology behind an OS disk list.

**What you get:** Print controller capabilities, redundancy and the drives attached to a selected storage subsystem.

**Requires:** System Storage; modern Controllers or legacy embedded StorageControllers.

**Operation:** Read. [DMTF Storage schema](https://redfish.dmtf.org/schemas/v1/Storage.json).

```python
"""051 · Map storage controllers to their drives
Requires: System Storage; modern Controllers or legacy embedded StorageControllers.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    storage = rf.storage()
    show(fields(storage, 'Id', 'Drives', 'Redundancy'))
    if storage.get('Controllers'):
        show([fields(c, 'Id', 'Model', 'FirmwareVersion', 'SupportedRAIDTypes', 'Status')
              for c in rf.members(rf.follow(storage, 'Controllers'))])
    else:
        show(storage.get('StorageControllers', []))
```

<a id="case-052"></a>

### 052 · Audit logical volumes and RAID levels

**Why Redfish fits:** Volume resources describe controller-managed storage even before the OS recognizes it.

**What you get:** List volume capacity, RAID type, encryption and health.

**Requires:** Storage Volumes collection.

**Operation:** Read. [DMTF Volume schema](https://redfish.dmtf.org/schemas/v1/Volume.json).

```python
"""052 · Audit logical volumes and RAID levels
Requires: Storage Volumes collection.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for storage in rf.members(rf.follow(rf.system(), 'Storage')):
        for volume in rf.members(rf.follow(storage, 'Volumes')):
            show(fields(volume, 'Id', 'Name', 'RAIDType', 'CapacityBytes', 'Encrypted', 'Status'))
```

<a id="case-053"></a>

### 053 · Plan physical storage capacity

**Why Redfish fits:** Physical drive capacity is useful for provisioning plans before filesystems or agents exist.

**What you get:** Total known drive capacity per controller, keeping missing capacity counts visible.

**Requires:** Storage Drives and Drive.CapacityBytes; raw capacity is not usable RAID/filesystem capacity.

**Operation:** Read. [DMTF Drive schema](https://redfish.dmtf.org/schemas/v1/Drive.json).

```python
"""053 · Plan physical storage capacity
Requires: Storage Drives and Drive.CapacityBytes; raw capacity is not usable RAID/filesystem capacity.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for storage in rf.members(rf.follow(rf.system(), 'Storage')):
        capacities = [rf.get(d).get('CapacityBytes') for d in storage.get('Drives', [])]
        known = [c for c in capacities if isinstance(c, int)]
        show({'storage': storage.get('Id'), 'raw_bytes': sum(known),
              'drives_with_unknown_capacity': len(capacities) - len(known)})
```

<a id="case-054"></a>

### 054 · Create a mirrored RAID volume

**Why Redfish fits:** Supported controllers can provision resilient boot storage through their advertised volume collection.

**What you get:** Preview creation of a RAID1 volume using an operator-supplied, controller-compatible payload.

**Requires:** An insertable Volumes collection and RAID1 support; VOLUME_CREATE_JSON must specify capacity/drive allocation as required by that controller.

**Operation:** Change. [DMTF Volume schema](https://redfish.dmtf.org/schemas/v1/Volume.json).

```python
"""054 · Create a mirrored RAID volume
Requires: An insertable Volumes collection and RAID1 support; VOLUME_CREATE_JSON must specify capacity/drive allocation as required by that controller.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    collection = rf.follow(rf.storage(), 'Volumes')
    payload = json.loads(required('VOLUME_CREATE_JSON'))
    # Example starting point: {"Name":"boot-mirror","RAIDType":"RAID1",
    # "CapacityBytes":100000000000}. Drive selection/creation rules vary.
    if not isinstance(payload, dict) or payload.get('RAIDType') != 'RAID1':
        raise ValueError('Supply a validated RAID1 creation payload for this controller')
    show(rf.write('POST', collection, payload))
```

<a id="case-055"></a>

### 055 · Initialize a newly provisioned volume

**Why Redfish fits:** The advertised volume action provides a standard way to request controller-side initialization.

**What you get:** Preview a fast initialization; executing it can destroy existing data.

**Requires:** Volume.Initialize supporting InitializeType Fast; select STORAGE_ID and VOLUME_ID.

**Operation:** Change. [DMTF Volume schema](https://redfish.dmtf.org/schemas/v1/Volume.json).

```python
"""055 · Initialize a newly provisioned volume
Requires: Volume.Initialize supporting InitializeType Fast; select STORAGE_ID and VOLUME_ID.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    volume = rf.volume()
    show(rf.action(volume, 'Volume.Initialize', {'InitializeType': 'Fast'}))
    # This can erase data. Follow any returned Task and verify completion.
```

<a id="case-056"></a>

### 056 · Follow a storage rebuild or background operation

**Why Redfish fits:** Volume operations expose controller progress without depending on host management software.

**What you get:** Read operation names, percentages and volume health during maintenance.

**Requires:** Volume.Operations populated by the controller for the operation in progress.

**Operation:** Read. [DMTF Volume schema](https://redfish.dmtf.org/schemas/v1/Volume.json).

```python
"""056 · Follow a storage rebuild or background operation
Requires: Volume.Operations populated by the controller for the operation in progress.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    volume = rf.volume()
    show(fields(volume, 'Id', 'Status', 'Operations'))
    # An empty Operations array means no advertised operation, not proof of all controller activity.
```

<a id="case-057"></a>

### 057 · Monitor SSD wear and NVMe error counters

**Why Redfish fits:** DriveMetrics can reveal endurance and media problems that capacity monitoring misses.

**What you get:** Read remaining media life, power-on hours, IO error counters and available NVMe SMART data.

**Requires:** Drive Metrics support; individual counters are optional.

**Operation:** Read. [DMTF DriveMetrics schema](https://redfish.dmtf.org/schemas/v1/DriveMetrics.json).

```python
"""057 · Monitor SSD wear and NVMe error counters
Requires: Drive Metrics support; individual counters are optional.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    metrics = rf.follow(rf.drive(), 'Metrics')
    show(fields(metrics, 'PredictedMediaLifeLeftPercent', 'PowerOnHours',
                'UncorrectableIOReadErrorCount', 'UncorrectableIOWriteErrorCount', 'NVMeSMART'))
```

<a id="case-058"></a>

### 058 · Identify the physical disk to replace

**Why Redfish fits:** A drive locator LED connects a remote diagnosis to the exact disk bay.

**What you get:** Preview activating the selected drive’s location indicator.

**Requires:** Writable Drive.LocationIndicatorActive; select DRIVE_ID.

**Operation:** Change. [DMTF Drive schema](https://redfish.dmtf.org/schemas/v1/Drive.json).

```python
"""058 · Identify the physical disk to replace
Requires: Writable Drive.LocationIndicatorActive; select DRIVE_ID.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    drive = rf.drive()
    if 'LocationIndicatorActive' not in drive:
        raise CapabilityError('Modern drive locator control is not advertised')
    show(rf.patch(drive, {'LocationIndicatorActive': True}))
```

<a id="case-059"></a>

### 059 · Designate a global hot spare

**Why Redfish fits:** Controller-backed hot-spare configuration supports recovery policies before a disk fails.

**What you get:** Preview assigning an eligible unused drive as a global hot spare.

**Requires:** Writable Drive.HotspareType and a controller supporting Global; verify the drive is unused.

**Operation:** Change. [DMTF Drive schema](https://redfish.dmtf.org/schemas/v1/Drive.json).

```python
"""059 · Designate a global hot spare
Requires: Writable Drive.HotspareType and a controller supporting Global; verify the drive is unused.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    drive = rf.drive()
    show(fields(drive, 'Id', 'HotspareType', 'Status'))
    show(rf.patch(drive, {'HotspareType': 'Global'}))
```

<a id="case-060"></a>

### 060 · Sanitize a drive before reuse

**Why Redfish fits:** An advertised hardware erase action can support a controlled decommissioning workflow.

**What you get:** Preview SecureErase with an explicitly chosen sanitization type; execution destroys data.

**Requires:** Drive.SecureErase; SANITIZATION_TYPE must match the advertised allowable values and your disposal policy.

**Operation:** Change. [DMTF Drive schema](https://redfish.dmtf.org/schemas/v1/Drive.json).

```python
"""060 · Sanitize a drive before reuse
Requires: Drive.SecureErase; SANITIZATION_TYPE must match the advertised allowable values and your disposal policy.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    drive = rf.drive()
    show(rf.action(drive, 'Drive.SecureErase', {
        'SanitizationType': required('SANITIZATION_TYPE'),
    }))
    # Verify Task completion and the platform’s erase guarantees before disposal.
```

## Networks & fabrics

<a id="case-061"></a>

### 061 · Audit management-network addresses

**Why Redfish fits:** The controller’s interfaces describe the independent management path rather than the host data network.

**What you get:** Read BMC MAC addresses, IP configuration and link status.

**Requires:** Manager EthernetInterfaces.

**Operation:** Read. [DMTF EthernetInterface schema](https://redfish.dmtf.org/schemas/v1/EthernetInterface.json).

```python
"""061 · Audit management-network addresses
Requires: Manager EthernetInterfaces.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for interface in rf.members(rf.follow(rf.manager(), 'EthernetInterfaces')):
        show(fields(interface, 'Id', 'MACAddress', 'IPv4Addresses', 'IPv6Addresses',
                    'DHCPv4', 'LinkStatus', 'FQDN'))
```

<a id="case-062"></a>

### 062 · Inventory host-network identity for provisioning

**Why Redfish fits:** MAC addresses discovered before installation can feed DHCP reservations and PXE provisioning.

**What you get:** List host Ethernet interface MAC addresses and advertised addresses.

**Requires:** ComputerSystem EthernetInterfaces; visibility of host IP configuration varies.

**Operation:** Read. [DMTF EthernetInterface schema](https://redfish.dmtf.org/schemas/v1/EthernetInterface.json).

```python
"""062 · Inventory host-network identity for provisioning
Requires: ComputerSystem EthernetInterfaces; visibility of host IP configuration varies.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for interface in rf.members(rf.follow(rf.system(), 'EthernetInterfaces')):
        show(fields(interface, 'Id', 'PermanentMACAddress', 'MACAddress',
                    'IPv4Addresses', 'IPv6Addresses'))
```

<a id="case-063"></a>

### 063 · Set a static BMC IPv4 address

**Why Redfish fits:** Remote management-network configuration can prepare servers for a dedicated operations subnet.

**What you get:** Preview disabling DHCPv4 and setting a static address; execution can interrupt this connection.

**Requires:** Writable manager EthernetInterface DHCPv4 and IPv4StaticAddresses; set INTERFACE_ID.

**Operation:** Change. [DMTF EthernetInterface schema](https://redfish.dmtf.org/schemas/v1/EthernetInterface.json).

```python
"""063 · Set a static BMC IPv4 address
Requires: Writable manager EthernetInterface DHCPv4 and IPv4StaticAddresses; set INTERFACE_ID.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    interface = rf.choose(rf.members(rf.follow(rf.manager(), 'EthernetInterfaces')), 'INTERFACE_ID')
    show(rf.patch(interface, {
        'DHCPv4': {'DHCPEnabled': False},
        'IPv4StaticAddresses': [{'Address': required('STATIC_IPV4'),
                                 'SubnetMask': required('IPV4_NETMASK'),
                                 'Gateway': required('IPV4_GATEWAY')}],
    }))
    # Plan alternate access before executing a management-network change.
```

<a id="case-064"></a>

### 064 · Configure BMC DNS resolvers

**Why Redfish fits:** A controller needs working DNS to reach named update, time and event destinations.

**What you get:** Preview a list of static DNS server addresses on the selected manager interface.

**Requires:** Writable EthernetInterface.StaticNameServers; DHCP-supplied settings may take precedence.

**Operation:** Change. [DMTF EthernetInterface schema](https://redfish.dmtf.org/schemas/v1/EthernetInterface.json).

```python
"""064 · Configure BMC DNS resolvers
Requires: Writable EthernetInterface.StaticNameServers; DHCP-supplied settings may take precedence.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    interface = rf.choose(rf.members(rf.follow(rf.manager(), 'EthernetInterfaces')), 'INTERFACE_ID')
    servers = json.loads(required('DNS_SERVERS_JSON'))
    if not isinstance(servers, list) or not all(isinstance(s, str) for s in servers):
        raise ValueError('DNS_SERVERS_JSON must be a JSON list of server addresses')
    show(rf.patch(interface, {'StaticNameServers': servers}))
```

<a id="case-065"></a>

### 065 · Inspect NIC physical link health

**Why Redfish fits:** Port resources distinguish a cabling or negotiated-speed problem from an application networking issue.

**What you get:** List port link state, speed and health on each supported physical NIC.

**Requires:** NetworkAdapter Ports collection; older services may expose NetworkPorts instead.

**Operation:** Read. [DMTF Port schema](https://redfish.dmtf.org/schemas/v1/Port.json).

```python
"""065 · Inspect NIC physical link health
Requires: NetworkAdapter Ports collection; older services may expose NetworkPorts instead.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for adapter in rf.members(rf.follow(rf.chassis(), 'NetworkAdapters')):
        for port in rf.members(rf.follow(adapter, 'Ports')):
            show(fields(port, 'Id', 'LinkStatus', 'LinkState',
                        'CurrentSpeedGbps', 'MaxSpeedGbps', 'Status'))
```

<a id="case-066"></a>

### 066 · Check NIC virtualization capability

**Why Redfish fits:** Hardware network-function metadata helps plan SR-IOV use before deploying a hypervisor.

**What you get:** Read virtual-function limits, enabled state and network function capabilities.

**Requires:** NetworkInterface.NetworkDeviceFunctions and advertised SR-IOV-related fields.

**Operation:** Read. [DMTF NetworkDeviceFunction schema](https://redfish.dmtf.org/schemas/v1/NetworkDeviceFunction.json).

```python
"""066 · Check NIC virtualization capability
Requires: NetworkInterface.NetworkDeviceFunctions and advertised SR-IOV-related fields.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for interface in rf.members(rf.follow(rf.system(), 'NetworkInterfaces')):
        for function in rf.members(rf.follow(interface, 'NetworkDeviceFunctions')):
            show(fields(function, 'Id', 'NetDevFuncType', 'NetDevFuncCapabilities',
                        'MaxVirtualFunctions', 'VirtualFunctionsEnabled', 'VirtualFunctionAllocation'))
```

<a id="case-067"></a>

### 067 · Configure a NIC function’s VLAN

**Why Redfish fits:** Supported adapters can stage hardware network-function settings before the host OS starts.

**What you get:** Preview enabling a VLAN on a selected network function; a reset may be required.

**Requires:** Writable NetworkDeviceFunction Ethernet.VLAN; set NETWORK_INTERFACE_ID and FUNCTION_ID.

**Operation:** Change. [DMTF NetworkDeviceFunction schema](https://redfish.dmtf.org/schemas/v1/NetworkDeviceFunction.json).

```python
"""067 · Configure a NIC function’s VLAN
Requires: Writable NetworkDeviceFunction Ethernet.VLAN; set NETWORK_INTERFACE_ID and FUNCTION_ID.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    interface = rf.choose(rf.members(rf.follow(rf.system(), 'NetworkInterfaces')), 'NETWORK_INTERFACE_ID')
    function = rf.choose(rf.members(rf.follow(interface, 'NetworkDeviceFunctions')), 'FUNCTION_ID')
    vlan = int(required('VLAN_ID'))
    if not 1 <= vlan <= 4094:
        raise ValueError('Choose a valid VLAN ID (1–4094)')
    target = rf.settings(function) if function.get('@Redfish.Settings') else function
    show(rf.patch(target, {'Ethernet': {'VLAN': {'VLANEnable': True, 'VLANId': vlan}}}))
```

<a id="case-068"></a>

### 068 · Audit iSCSI boot configuration

**Why Redfish fits:** Out-of-band NIC function data can explain why a diskless host cannot find its boot target.

**What you get:** Read advertised iSCSI initiator and target configuration, with secrets redacted.

**Requires:** NetworkDeviceFunction.iSCSIBoot on an adapter supporting iSCSI boot.

**Operation:** Read. [DMTF NetworkDeviceFunction schema](https://redfish.dmtf.org/schemas/v1/NetworkDeviceFunction.json).

```python
"""068 · Audit iSCSI boot configuration
Requires: NetworkDeviceFunction.iSCSIBoot on an adapter supporting iSCSI boot.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for interface in rf.members(rf.follow(rf.system(), 'NetworkInterfaces')):
        for function in rf.members(rf.follow(interface, 'NetworkDeviceFunctions')):
            show({'function': function.get('Id'), 'boot_mode': function.get('BootMode'),
                  'iscsi_boot': function.get('iSCSIBoot')})
```

<a id="case-069"></a>

### 069 · Map managed fabric switches and endpoints

**Why Redfish fits:** Redfish fabric resources connect supported switches and endpoints through a common resource model.

**What you get:** Read each fabric’s type and its advertised switch/endpoint collections.

**Requires:** ServiceRoot Fabrics; supported fabric management is separate from ordinary host networking.

**Operation:** Read. [DMTF Fabric schema](https://redfish.dmtf.org/schemas/v1/Fabric.json).

```python
"""069 · Map managed fabric switches and endpoints
Requires: ServiceRoot Fabrics; supported fabric management is separate from ordinary host networking.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for fabric in rf.members(rf.follow(rf.root, 'Fabrics')):
        show(fields(fabric, 'Id', 'FabricType', 'Status'))
        if fabric.get('Switches'):
            show([fields(s, 'Id', 'Model', 'SwitchType', 'Status')
                  for s in rf.members(rf.follow(fabric, 'Switches'))])
        if fabric.get('Endpoints'):
            show([fields(e, 'Id', 'EndpointProtocol', 'ConnectedEntities')
                  for e in rf.members(rf.follow(fabric, 'Endpoints'))])
```

<a id="case-070"></a>

### 070 · Configure the BMC’s time servers

**Why Redfish fits:** Consistent controller time improves the reliability of hardware incident timelines across a fleet.

**What you get:** Preview enabling NTP and setting its configured servers.

**Requires:** Writable ManagerNetworkProtocol.NTP.NTPServers and ProtocolEnabled.

**Operation:** Change. [DMTF ManagerNetworkProtocol schema](https://redfish.dmtf.org/schemas/v1/ManagerNetworkProtocol.json).

```python
"""070 · Configure the BMC’s time servers
Requires: Writable ManagerNetworkProtocol.NTP.NTPServers and ProtocolEnabled.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    protocols = rf.follow(rf.manager(), 'NetworkProtocol')
    servers = json.loads(required('NTP_SERVERS_JSON'))
    if not isinstance(servers, list) or not all(isinstance(s, str) for s in servers):
        raise ValueError('NTP_SERVERS_JSON must be a JSON list of server names or addresses')
    show(rf.patch(protocols, {'NTP': {'ProtocolEnabled': True, 'NTPServers': servers}}))
```

## Security & access

<a id="case-071"></a>

### 071 · Audit local management accounts

**Why Redfish fits:** A central account inventory helps reveal stale access on many independent controllers.

**What you get:** List account names, roles, enabled state and password-change requirements.

**Requires:** AccountService Accounts and permission to enumerate accounts.

**Operation:** Read. [DMTF ManagerAccount schema](https://redfish.dmtf.org/schemas/v1/ManagerAccount.json).

```python
"""071 · Audit local management accounts
Requires: AccountService Accounts and permission to enumerate accounts.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    accounts = rf.follow(rf.root, 'AccountService')
    show([fields(a, 'Id', 'UserName', 'RoleId', 'Enabled', 'Locked', 'PasswordChangeRequired')
          for a in rf.members(rf.follow(accounts, 'Accounts'))])
```

<a id="case-072"></a>

### 072 · Create a dedicated read-only observer account

**Why Redfish fits:** A separate least-privilege identity lets telemetry collectors avoid sharing an administrator account.

**What you get:** Preview creation with the advertised ReadOnly role and an operator-supplied password.

**Requires:** Insertable Accounts and a supported ReadOnly role; account-creation privileges are required.

**Operation:** Change. [DMTF ManagerAccount schema](https://redfish.dmtf.org/schemas/v1/ManagerAccount.json).

```python
"""072 · Create a dedicated read-only observer account
Requires: Insertable Accounts and a supported ReadOnly role; account-creation privileges are required.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    service = rf.follow(rf.root, 'AccountService')
    roles = rf.members(rf.follow(service, 'Roles'))
    if not any(r.get('Id') == 'ReadOnly' or r.get('RoleId') == 'ReadOnly' for r in roles):
        raise CapabilityError('ReadOnly role is not advertised')
    show(rf.write('POST', rf.follow(service, 'Accounts'), {
        'UserName': required('NEW_ACCOUNT_NAME'), 'Password': required('NEW_ACCOUNT_PASSWORD'),
        'RoleId': 'ReadOnly', 'Enabled': True,
    }))
```

<a id="case-073"></a>

### 073 · Disable a departed user’s BMC account

**Why Redfish fits:** Hardware management access needs its own offboarding because it persists outside the host OS.

**What you get:** Preview disabling a specifically selected account.

**Requires:** Writable ManagerAccount.Enabled; set ACCOUNT_ID and preserve another administrative access path.

**Operation:** Change. [DMTF ManagerAccount schema](https://redfish.dmtf.org/schemas/v1/ManagerAccount.json).

```python
"""073 · Disable a departed user’s BMC account
Requires: Writable ManagerAccount.Enabled; set ACCOUNT_ID and preserve another administrative access path.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    service = rf.follow(rf.root, 'AccountService')
    account = rf.choose(rf.members(rf.follow(service, 'Accounts')), 'ACCOUNT_ID')
    show({'selected_account': fields(account, 'Id', 'UserName', 'RoleId')})
    show(rf.patch(account, {'Enabled': False}))
```

<a id="case-074"></a>

### 074 · Rotate a local management password

**Why Redfish fits:** A consistent account API can be integrated into a controlled credential-rotation workflow.

**What you get:** Preview a password update for a selected account without printing the new secret.

**Requires:** Writable ManagerAccount.Password; some services require ChangePassword for self-service changes.

**Operation:** Change. [DMTF ManagerAccount schema](https://redfish.dmtf.org/schemas/v1/ManagerAccount.json).

```python
"""074 · Rotate a local management password
Requires: Writable ManagerAccount.Password; some services require ChangePassword for self-service changes.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    service = rf.follow(rf.root, 'AccountService')
    account = rf.choose(rf.members(rf.follow(service, 'Accounts')), 'ACCOUNT_ID')
    show(rf.patch(account, {'Password': required('NEW_ACCOUNT_PASSWORD')}))
```

<a id="case-075"></a>

### 075 · Review the privileges behind each role

**Why Redfish fits:** Role resources make controller access policies inspectable instead of relying only on role names.

**What you get:** List standard and OEM privileges for each advertised role.

**Requires:** AccountService Roles and permission to read Role resources.

**Operation:** Read. [DMTF Role schema](https://redfish.dmtf.org/schemas/v1/Role.json).

```python
"""075 · Review the privileges behind each role
Requires: AccountService Roles and permission to read Role resources.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    service = rf.follow(rf.root, 'AccountService')
    show([fields(r, 'Id', 'RoleId', 'IsPredefined', 'AssignedPrivileges', 'OemPrivileges')
          for r in rf.members(rf.follow(service, 'Roles'))])
```

<a id="case-076"></a>

### 076 · Standardize account lockout behavior

**Why Redfish fits:** A controller-wide lockout policy reduces inconsistent protection across an operations fleet.

**What you get:** Preview a chosen failed-login threshold and lockout duration.

**Requires:** Writable AccountService lockout properties; LOCKOUT_THRESHOLD and LOCKOUT_SECONDS follow your policy.

**Operation:** Change. [DMTF AccountService schema](https://redfish.dmtf.org/schemas/v1/AccountService.json).

```python
"""076 · Standardize account lockout behavior
Requires: Writable AccountService lockout properties; LOCKOUT_THRESHOLD and LOCKOUT_SECONDS follow your policy.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    service = rf.follow(rf.root, 'AccountService')
    threshold, seconds = int(required('LOCKOUT_THRESHOLD')), int(required('LOCKOUT_SECONDS'))
    if threshold < 1 or seconds < 1:
        raise ValueError('Choose positive lockout values supported by your BMC')
    show(rf.patch(service, {'AccountLockoutThreshold': threshold, 'AccountLockoutDuration': seconds}))
```

<a id="case-077"></a>

### 077 · Audit UEFI Secure Boot state

**Why Redfish fits:** Firmware security state can be checked before trusting a newly provisioned host.

**What you get:** Read configured enablement, current-boot status and Secure Boot mode.

**Requires:** ComputerSystem SecureBoot link; this is configuration evidence, not remote attestation.

**Operation:** Read. [DMTF SecureBoot schema](https://redfish.dmtf.org/schemas/v1/SecureBoot.json).

```python
"""077 · Audit UEFI Secure Boot state
Requires: ComputerSystem SecureBoot link; this is configuration evidence, not remote attestation.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    secure_boot = rf.follow(rf.system(), 'SecureBoot')
    show(fields(secure_boot, 'SecureBootEnable', 'SecureBootCurrentBoot', 'SecureBootMode'))
```

<a id="case-078"></a>

### 078 · Enable Secure Boot for a prepared platform

**Why Redfish fits:** Redfish can stage a firmware security setting without manually entering every server’s setup screen.

**What you get:** Preview SecureBootEnable=true; compatible signed boot components and a reset may be required.

**Requires:** Writable SecureBootEnable; validate signing keys and OS compatibility before execution.

**Operation:** Change. [DMTF SecureBoot schema](https://redfish.dmtf.org/schemas/v1/SecureBoot.json).

```python
"""078 · Enable Secure Boot for a prepared platform
Requires: Writable SecureBootEnable; validate signing keys and OS compatibility before execution.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    secure_boot = rf.follow(rf.system(), 'SecureBoot')
    show(rf.patch(secure_boot, {'SecureBootEnable': True}))
```

<a id="case-079"></a>

### 079 · Find expiring BMC HTTPS certificates

**Why Redfish fits:** Certificate inventory allows management-plane TLS expiry to be monitored like other infrastructure.

**What you get:** List HTTPS certificate subjects, issuers and validity dates.

**Requires:** Manager NetworkProtocol HTTPS.Certificates.

**Operation:** Read. [DMTF Certificate schema](https://redfish.dmtf.org/schemas/v1/Certificate.json).

```python
"""079 · Find expiring BMC HTTPS certificates
Requires: Manager NetworkProtocol HTTPS.Certificates.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    protocols = rf.follow(rf.manager(), 'NetworkProtocol')
    https = protocols.get('HTTPS', {})
    for certificate in rf.members(rf.follow(https, 'Certificates')):
        show(fields(certificate, 'Id', 'Subject', 'Issuer', 'ValidNotBefore', 'ValidNotAfter'))
```

<a id="case-080"></a>

### 080 · Replace a management HTTPS certificate

**Why Redfish fits:** CertificateService provides a discoverable way to renew a controller’s management certificate.

**What you get:** Preview replacing a selected HTTPS certificate with a trusted PEM certificate.

**Requires:** CertificateService.ReplaceCertificate; PEM must match the controller’s key/CSR and trust configuration.

**Operation:** Change. [DMTF CertificateService schema](https://redfish.dmtf.org/schemas/v1/CertificateService.json).

```python
"""080 · Replace a management HTTPS certificate
Requires: CertificateService.ReplaceCertificate; PEM must match the controller’s key/CSR and trust configuration.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show
from pathlib import Path

with RecipeClient.from_env() as rf:
    service = rf.follow(rf.root, 'CertificateService')
    protocols = rf.follow(rf.manager(), 'NetworkProtocol')
    certificate = rf.choose(rf.members(rf.follow(protocols.get('HTTPS', {}), 'Certificates')), 'CERTIFICATE_ID')
    pem = Path(required('CERTIFICATE_PEM_FILE')).read_text()
    show(rf.action(service, 'CertificateService.ReplaceCertificate', {
        'CertificateUri': {'@odata.id': rf.path(certificate)},
        'CertificateType': 'PEM', 'CertificateString': pem,
    }))
```

## Facilities & fleet

<a id="case-081"></a>

### 081 · Assign an asset tag during fleet enrollment

**Why Redfish fits:** A writable asset tag binds the physical chassis to an organization’s inventory identifier.

**What you get:** Preview assigning a chosen chassis asset tag.

**Requires:** Writable Chassis.AssetTag; ASSET_TAG is your inventory identifier.

**Operation:** Change. [DMTF Chassis schema](https://redfish.dmtf.org/schemas/v1/Chassis.json).

```python
"""081 · Assign an asset tag during fleet enrollment
Requires: Writable Chassis.AssetTag; ASSET_TAG is your inventory identifier.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    chassis = rf.chassis()
    show(rf.patch(chassis, {'AssetTag': required('ASSET_TAG')}))
```

<a id="case-082"></a>

### 082 · Inventory Redfish-capable rack PDUs

**Why Redfish fits:** PowerEquipment extends a common inventory approach to compatible rack power infrastructure.

**What you get:** List rack PDU model, serial number, capacity and location.

**Requires:** A facility/PDU controller exposing PowerEquipment.RackPDUs; ordinary server BMCs may omit it.

**Operation:** Read. [DMTF PowerEquipment schema](https://redfish.dmtf.org/schemas/v1/PowerEquipment.json).

```python
"""082 · Inventory Redfish-capable rack PDUs
Requires: A facility/PDU controller exposing PowerEquipment.RackPDUs; ordinary server BMCs may omit it.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    equipment = rf.follow(rf.root, 'PowerEquipment')
    show([fields(p, 'Id', 'Model', 'SerialNumber', 'PowerCapacityVA', 'Location', 'Status')
          for p in rf.members(rf.follow(equipment, 'RackPDUs'))])
```

<a id="case-083"></a>

### 083 · Measure power at individual rack outlets

**Why Redfish fits:** Outlet measurements help attribute physical power use to equipment connected to a compatible PDU.

**What you get:** Read per-outlet power, energy and electrical consumer labels.

**Requires:** Redfish RackPDU Outlets and metered readings; set PDU_ID.

**Operation:** Read. [DMTF Outlet schema](https://redfish.dmtf.org/schemas/v1/Outlet.json).

```python
"""083 · Measure power at individual rack outlets
Requires: Redfish RackPDU Outlets and metered readings; set PDU_ID.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    equipment = rf.follow(rf.root, 'PowerEquipment')
    pdu = rf.choose(rf.members(rf.follow(equipment, 'RackPDUs')), 'PDU_ID')
    for outlet in rf.members(rf.follow(pdu, 'Outlets')):
        show(fields(outlet, 'Id', 'PowerWatts', 'EnergykWh', 'ElectricalConsumerNames', 'PowerState'))
```

<a id="case-084"></a>

### 084 · Find overloaded PDU branches

**Why Redfish fits:** Circuit measurements reveal rack electrical constraints that no single server can see.

**What you get:** Read branch current, rated current, load percentage and breaker state.

**Requires:** RackPDU Branches collection with Circuit measurements.

**Operation:** Read. [DMTF Circuit schema](https://redfish.dmtf.org/schemas/v1/Circuit.json).

```python
"""084 · Find overloaded PDU branches
Requires: RackPDU Branches collection with Circuit measurements.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    equipment = rf.follow(rf.root, 'PowerEquipment')
    pdu = rf.choose(rf.members(rf.follow(equipment, 'RackPDUs')), 'PDU_ID')
    for branch in rf.members(rf.follow(pdu, 'Branches')):
        show(fields(branch, 'Id', 'CurrentAmps', 'RatedCurrentAmps',
                    'PowerLoadPercent', 'BreakerState', 'Status'))
```

<a id="case-085"></a>

### 085 · Power-cycle a selected PDU outlet remotely

**Why Redfish fits:** A switched PDU can recover equipment whose own management controller is unreachable.

**What you get:** Preview PowerCycle for a verified outlet; execution removes power from its connected equipment.

**Requires:** Outlet.PowerControl supporting PowerCycle; confirm PDU_ID, OUTLET_ID and cabling ownership.

**Operation:** Change. [DMTF Outlet schema](https://redfish.dmtf.org/schemas/v1/Outlet.json).

```python
"""085 · Power-cycle a selected PDU outlet remotely
Requires: Outlet.PowerControl supporting PowerCycle; confirm PDU_ID, OUTLET_ID and cabling ownership.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    equipment = rf.follow(rf.root, 'PowerEquipment')
    pdu = rf.choose(rf.members(rf.follow(equipment, 'RackPDUs')), 'PDU_ID')
    outlet = rf.choose(rf.members(rf.follow(pdu, 'Outlets')), 'OUTLET_ID')
    show(fields(outlet, 'Id', 'ElectricalConsumerNames', 'UserLabel'))
    show(rf.action(outlet, 'Outlet.PowerControl', {'PowerState': 'PowerCycle'}))
```

<a id="case-086"></a>

### 086 · Inventory liquid-cooling distribution units

**Why Redfish fits:** ThermalEquipment provides a hardware management model for compatible cooling infrastructure in dense racks.

**What you get:** List CDU capacity, coolant information and health.

**Requires:** A cooling/facility controller exposing ThermalEquipment.CDUs.

**Operation:** Read. [DMTF CoolingUnit schema](https://redfish.dmtf.org/schemas/v1/CoolingUnit.json).

```python
"""086 · Inventory liquid-cooling distribution units
Requires: A cooling/facility controller exposing ThermalEquipment.CDUs.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    equipment = rf.follow(rf.root, 'ThermalEquipment')
    show([fields(c, 'Id', 'Model', 'CoolingCapacityWatts', 'Coolant', 'Status')
          for c in rf.members(rf.follow(equipment, 'CDUs'))])
```

<a id="case-087"></a>

### 087 · Monitor coolant flow and heat removal

**Why Redfish fits:** Coolant connector measurements help explain thermal problems in liquid-cooled infrastructure.

**What you get:** Read flow, temperatures, pressure difference and heat removed from advertised secondary connectors.

**Requires:** CoolingUnit.SecondaryCoolantConnectors with measurements; set CDU_ID.

**Operation:** Read. [DMTF CoolantConnector schema](https://redfish.dmtf.org/schemas/v1/CoolantConnector.json).

```python
"""087 · Monitor coolant flow and heat removal
Requires: CoolingUnit.SecondaryCoolantConnectors with measurements; set CDU_ID.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    equipment = rf.follow(rf.root, 'ThermalEquipment')
    cdu = rf.choose(rf.members(rf.follow(equipment, 'CDUs')), 'CDU_ID')
    for connector in rf.members(rf.follow(cdu, 'SecondaryCoolantConnectors')):
        show(fields(connector, 'Id', 'FlowLitersPerMinute', 'SupplyTemperatureCelsius',
                    'ReturnTemperatureCelsius', 'DeltaPressurekPa', 'HeatRemovedkW', 'Status'))
```

<a id="case-088"></a>

### 088 · Detect a leak in a liquid-cooled chassis

**Why Redfish fits:** Physical leak detectors provide an urgent hardware signal outside the host application stack.

**What you get:** Read detector state, physical context and health for the selected chassis.

**Requires:** Chassis LeakDetectors collection; earlier models may link through ThermalSubsystem.LeakDetection.

**Operation:** Read. [DMTF LeakDetector schema](https://redfish.dmtf.org/schemas/v1/LeakDetector.json).

```python
"""088 · Detect a leak in a liquid-cooled chassis
Requires: Chassis LeakDetectors collection; earlier models may link through ThermalSubsystem.LeakDetection.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    for detector in rf.members(rf.follow(rf.chassis(), 'LeakDetectors')):
        show(fields(detector, 'Id', 'DetectorState', 'LeakDetectorType',
                    'PhysicalContext', 'Status'))
```

<a id="case-089"></a>

### 089 · Watch rack intake temperature and humidity

**Why Redfish fits:** Environmental measurements help connect room conditions to server thermal health.

**What you get:** Read advertised ambient temperature, humidity and dew-point excerpts.

**Requires:** Chassis EnvironmentMetrics and appropriate environmental sensors; some equipment omits these readings.

**Operation:** Read. [DMTF EnvironmentMetrics schema](https://redfish.dmtf.org/schemas/v1/EnvironmentMetrics.json).

```python
"""089 · Watch rack intake temperature and humidity
Requires: Chassis EnvironmentMetrics and appropriate environmental sensors; some equipment omits these readings.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    environment = rf.follow(rf.chassis(), 'EnvironmentMetrics')
    show(fields(environment, 'AmbientTemperatureCelsius', 'HumidityPercent',
                'DewPointCelsius', 'DewPointProximityCelsius'))
```

<a id="case-090"></a>

### 090 · Find field-replaceable assembly part numbers

**Why Redfish fits:** Assembly inventory helps order the correct spare for a physical maintenance visit.

**What you get:** List assembly members, part numbers, spare part numbers and serial identities.

**Requires:** Chassis Assembly with Assemblies array.

**Operation:** Read. [DMTF Assembly schema](https://redfish.dmtf.org/schemas/v1/Assembly.json).

```python
"""090 · Find field-replaceable assembly part numbers
Requires: Chassis Assembly with Assemblies array.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    assembly = rf.follow(rf.chassis(), 'Assembly')
    show([fields(a, 'MemberId', 'Name', 'PartNumber', 'SparePartNumber',
                 'SerialNumber', 'Version', 'Status') for a in assembly.get('Assemblies', [])])
```

## Events & OpenTelemetry

<a id="case-091"></a>

### 091 · Subscribe a hardware-event webhook

**Why Redfish fits:** EventService pushes faults soon after they occur, reducing reliance on repeated log polling.

**What you get:** Preview a Redfish event subscription to an operator-controlled HTTPS receiver.

**Requires:** EventService Subscriptions, callback reachability and receiver TLS trust; production receivers must validate and deduplicate events.

**Operation:** Change. [DMTF EventDestination schema](https://redfish.dmtf.org/schemas/v1/EventDestination.json).

```python
"""091 · Subscribe a hardware-event webhook
Requires: EventService Subscriptions, callback reachability and receiver TLS trust; production receivers must validate and deduplicate events.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    service = rf.follow(rf.root, 'EventService')
    destination = required('EVENT_RECEIVER_URL')
    if not destination.startswith('https://'):
        raise ValueError('Use a trusted HTTPS event receiver')
    show(rf.write('POST', rf.follow(service, 'Subscriptions'), {
        'Destination': destination, 'Protocol': 'Redfish',
        'EventFormatType': 'Event', 'Context': 'hardware-observer',
    }))
```

<a id="case-092"></a>

### 092 · Export hardware fault history as OTel logs

**Why Redfish fits:** Redfish supplies hardware evidence while the OTel SDK routes it into the same log system used by applications.

**What you get:** Export a one-shot set of BMC log entries with source time, severity and stable server identity.

**Requires:** Manager LogServices plus the installed OTel SDK; continuous collectors must checkpoint/deduplicate entry IDs.

**Operation:** OpenTelemetry. [DMTF LogEntry schema](https://redfish.dmtf.org/schemas/v1/LogEntry.json).

```python
"""092 · Export hardware fault history as OTel logs
Requires: Manager LogServices plus the installed OTel SDK; continuous collectors must checkpoint/deduplicate entry IDs.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show
from redfish_lab.recipe_telemetry import RecipeTelemetry

with RecipeClient.from_env() as rf:
    with RecipeTelemetry(rf.system()) as telemetry:
        for log in rf.members(rf.follow(rf.manager(), 'LogServices')):
            for entry in rf.members(rf.follow(log, 'Entries')):
                telemetry.log(entry.get('Message', 'Hardware event'),
                              severity=entry.get('Severity', 'OK'), timestamp=entry.get('Created'),
                              attributes={'redfish.log.id': log.get('Id', ''),
                                          'redfish.entry.id': entry.get('Id', ''),
                                          'redfish.message_id': entry.get('MessageId', '')})
    # Console by default; OTEL_EXPORTER_OTLP_ENDPOINT sends HTTP/protobuf to a Collector.
```

<a id="case-093"></a>

### 093 · Discover periodic hardware telemetry reports

**Why Redfish fits:** Report definitions describe the measurements and schedules a controller can publish.

**What you get:** List report types, schedules, metric properties and report actions before choosing a collection strategy.

**Requires:** TelemetryService.MetricReportDefinitions; support and minimum intervals vary.

**Operation:** Read. [DMTF MetricReportDefinition schema](https://redfish.dmtf.org/schemas/v1/MetricReportDefinition.json).

```python
"""093 · Discover periodic hardware telemetry reports
Requires: TelemetryService.MetricReportDefinitions; support and minimum intervals vary.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show

with RecipeClient.from_env() as rf:
    service = rf.follow(rf.root, 'TelemetryService')
    show(fields(service, 'MinCollectionInterval', 'MaxReports'))
    show([fields(d, 'Id', 'MetricReportDefinitionType', 'Schedule', 'MetricProperties',
                 'Metrics', 'ReportActions', 'MetricReportDefinitionEnabled')
          for d in rf.members(rf.follow(service, 'MetricReportDefinitions'))])
```

<a id="case-094"></a>

### 094 · Convert a MetricReport to OTel gauges

**Why Redfish fits:** An adapter can translate BMC metric reports into observable measurements for a shared backend.

**What you get:** Export numeric current readings with explicitly supplied units; report timestamps are printed separately.

**Requires:** TelemetryService.MetricReports; METRIC_UNITS_JSON maps MetricId to verified units from MetricDefinitions. Use current readings, not accumulated history.

**Operation:** OpenTelemetry. [DMTF MetricReport schema](https://redfish.dmtf.org/schemas/v1/MetricReport.json).

```python
"""094 · Convert a MetricReport to OTel gauges
Requires: TelemetryService.MetricReports; METRIC_UNITS_JSON maps MetricId to verified units from MetricDefinitions. Use current readings, not accumulated history.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show
import re
from redfish_lab.recipe_telemetry import RecipeTelemetry

with RecipeClient.from_env() as rf:
    units = json.loads(required('METRIC_UNITS_JSON'))  # e.g. {"CPU1Temp":"Cel"}
    service = rf.follow(rf.root, 'TelemetryService')
    with RecipeTelemetry(rf.system()) as telemetry:
        for report in rf.members(rf.follow(service, 'MetricReports')):
            for point in report.get('MetricValues', []):
                metric_id = point.get('MetricId')
                if metric_id not in units:
                    continue  # Never guess units from a name.
                try:
                    value = float(point.get('MetricValue'))
                except (TypeError, ValueError):
                    continue
                name = 'redfish.report.' + re.sub(r'[^a-zA-Z0-9_.-]', '_', metric_id)[:200]
                telemetry.gauge(name, value, units[metric_id],
                                {'redfish.metric.id': metric_id, 'redfish.report.id': report.get('Id', '')})
                show({'metric': metric_id, 'source_timestamp': point.get('Timestamp')})
    # Gauges use collection/export time; replaying historical samples needs a different adapter.
```

<a id="case-095"></a>

### 095 · Export temperature into an OTel dashboard

**Why Redfish fits:** A Python adapter makes Redfish temperatures available to the same metrics backend that monitors software.

**What you get:** Export valid Celsius sensor readings as real OTel observable gauges.

**Requires:** Temperature Sensors in Cel plus the OTel SDK; missing readings are skipped rather than replaced with zero.

**Operation:** OpenTelemetry. [DMTF Sensor schema](https://redfish.dmtf.org/schemas/v1/Sensor.json).

```python
"""095 · Export temperature into an OTel dashboard
Requires: Temperature Sensors in Cel plus the OTel SDK; missing readings are skipped rather than replaced with zero.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show
from redfish_lab.recipe_telemetry import RecipeTelemetry

with RecipeClient.from_env() as rf:
    with RecipeTelemetry(rf.system()) as telemetry:
        for sensor in rf.sensors('Temperature'):
            reading = sensor.get('Reading')
            if sensor.get('ReadingUnits') == 'Cel' and isinstance(reading, (int, float)):
                telemetry.gauge('redfish.hardware.temperature', reading, 'Cel',
                                {'redfish.sensor.id': sensor.get('Id', '')})
                show(fields(sensor, 'Id', 'ReadingTime'))
    # Set OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318 for the optional Collector.
```

<a id="case-096"></a>

### 096 · Export physical power into OTel metrics

**Why Redfish fits:** Redfish watt readings complement application throughput when evaluating energy use.

**What you get:** Export watt-valued power sensors as OTel gauges with stable host and sensor identities.

**Requires:** Power Sensors in W; collection interval and freshness must suit the equipment.

**Operation:** OpenTelemetry. [DMTF Sensor schema](https://redfish.dmtf.org/schemas/v1/Sensor.json).

```python
"""096 · Export physical power into OTel metrics
Requires: Power Sensors in W; collection interval and freshness must suit the equipment.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show
from redfish_lab.recipe_telemetry import RecipeTelemetry

with RecipeClient.from_env() as rf:
    with RecipeTelemetry(rf.system()) as telemetry:
        for sensor in rf.sensors('Power'):
            reading = sensor.get('Reading')
            if sensor.get('ReadingUnits') == 'W' and isinstance(reading, (int, float)):
                telemetry.gauge('redfish.hardware.power', reading, 'W',
                                {'redfish.sensor.id': sensor.get('Id', '')})
```

<a id="case-097"></a>

### 097 · Give hardware and application signals a shared identity

**Why Redfish fits:** A system UUID or serial number can join hardware readings to the application running on that physical server.

**What you get:** Build an OTel Resource with stable host.id and a separate service instance identity.

**Requires:** System UUID or SerialNumber; the application must use the same verified host.id mapping.

**Operation:** OpenTelemetry. [DMTF ComputerSystem schema](https://redfish.dmtf.org/schemas/v1/ComputerSystem.json).

```python
"""097 · Give hardware and application signals a shared identity
Requires: System UUID or SerialNumber; the application must use the same verified host.id mapping.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show
from redfish_lab.recipe_telemetry import hardware_resource

with RecipeClient.from_env() as rf:
    resource = hardware_resource(rf.system(), service_name='hardware-observer')
    show(dict(resource.attributes))
    # Configure the application SDK with this same host.id (and its own service.name).
    # Match by identity and time; hardware events do not automatically have request trace IDs.
```

<a id="case-098"></a>

### 098 · Trace the latency of a hardware polling request

**Why Redfish fits:** Instrumenting the adapter reveals slow or failing BMC reads in the observability pipeline itself.

**What you get:** Export a real span covering an actual HTTPS sensor read and its measured duration.

**Requires:** Sensors plus the OTel SDK; this is an adapter request trace, not a trace emitted by Redfish.

**Operation:** OpenTelemetry. [DMTF Sensor schema](https://redfish.dmtf.org/schemas/v1/Sensor.json).

```python
"""098 · Trace the latency of a hardware polling request
Requires: Sensors plus the OTel SDK; this is an adapter request trace, not a trace emitted by Redfish.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show
import time
from redfish_lab.recipe_telemetry import RecipeTelemetry

with RecipeClient.from_env() as rf:
    system = rf.system()
    chassis = rf.chassis()
    with RecipeTelemetry(system) as telemetry:
        with telemetry.tracer.start_as_current_span('redfish.poll.sensors') as span:
            started = time.perf_counter()
            sensors = rf.members(rf.follow(chassis, 'Sensors'))
            span.set_attribute('redfish.sensor.count', len(sensors))
            span.set_attribute('redfish.poll.duration_ms', (time.perf_counter() - started) * 1000)
        show({'sensors_read': len(sensors)})
```

<a id="case-099"></a>

### 099 · Alert when hardware telemetry is stale

**Why Redfish fits:** A healthy-looking last value is misleading if a controller has stopped supplying fresh samples.

**What you get:** Compare source ReadingTime with current UTC and export warning logs for stale or unparseable samples.

**Requires:** Sensors with timezone-qualified ReadingTime and synchronized clocks; SAMPLE_MAX_AGE_SECONDS sets the threshold.

**Operation:** OpenTelemetry. [DMTF Sensor schema](https://redfish.dmtf.org/schemas/v1/Sensor.json).

```python
"""099 · Alert when hardware telemetry is stale
Requires: Sensors with timezone-qualified ReadingTime and synchronized clocks; SAMPLE_MAX_AGE_SECONDS sets the threshold.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show
import time
from redfish_lab.recipe_telemetry import RecipeTelemetry, source_timestamp

with RecipeClient.from_env() as rf:
    limit = float(required('SAMPLE_MAX_AGE_SECONDS'))
    if limit <= 0:
        raise ValueError('Choose a positive freshness limit')
    with RecipeTelemetry(rf.system()) as telemetry:
        for sensor in rf.sensors():
            stamp = source_timestamp(sensor.get('ReadingTime'))
            age = (time.time_ns() - stamp) / 1e9 if stamp is not None else None
            if age is None or age > limit or age < -5:
                telemetry.log('Missing, stale or future hardware sample', severity='Warning',
                              attributes={'redfish.sensor.id': sensor.get('Id', ''),
                                          'redfish.sample.time': sensor.get('ReadingTime') or 'unknown'})
```

<a id="case-100"></a>

### 100 · Correlate hardware heat with application request latency

**Why Redfish fits:** Redfish supplies temperatures and OTel supplies measured application spans, allowing a backend to compare them by server and time.

**What you get:** Export hardware gauges and a span around a real instrumented work function under the same host identity.

**Requires:** Temperature Sensors, OTel SDK and application instrumentation on the same mapped host; correlation alone does not prove causation.

**Operation:** OpenTelemetry. [DMTF Sensor schema](https://redfish.dmtf.org/schemas/v1/Sensor.json).

```python
"""100 · Correlate hardware heat with application request latency
Requires: Temperature Sensors, OTel SDK and application instrumentation on the same mapped host; correlation alone does not prove causation.
"""
# Install this project first: python -m pip install -e .
# Set BMC_URL, BMC_USERNAME, BMC_PASSWORD; TLS is verified.
# Writes are previews unless ALLOW_REDFISH_WRITES=1.
import json
import os
from redfish_lab.recipe_client import RecipeClient, CapabilityError, fields, required, show
from redfish_lab.recipe_telemetry import RecipeTelemetry

with RecipeClient.from_env() as rf:
    def application_work():
        # Run on the managed host; this is local work, not remote execution by Redfish.
        # Replace this measured demonstration with your actual application request.
        return sum(i * i for i in range(100_000))

    with RecipeTelemetry(rf.system()) as telemetry:
        for sensor in rf.sensors('Temperature'):
            value = sensor.get('Reading')
            if sensor.get('ReadingUnits') == 'Cel' and isinstance(value, (int, float)):
                telemetry.gauge('redfish.hardware.temperature', value, 'Cel',
                                {'redfish.sensor.id': sensor.get('Id', '')})
        with telemetry.tracer.start_as_current_span('application.work'):
            result = application_work()
        show({'result': result, 'join': 'host.id + overlapping time window'})
    # In production, instrument the application separately with its own service.name.
```
