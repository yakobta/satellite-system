-- Useful SQL Queries for Satellite Telemetry Analysis

-- 1. Mission Health Summary
SELECT 
    satellite_id,
    COUNT(*) as total_packets,
    MIN(timestamp) as mission_start,
    MAX(timestamp) as last_contact,
    AVG(battery_level) as avg_battery,
    MIN(battery_level) as min_battery,
    AVG(thermal_main_bus) as avg_temp,
    MAX(thermal_main_bus) as max_temp,
    AVG(signal_strength) as avg_signal,
    MIN(signal_strength) as min_signal
FROM telemetry
GROUP BY satellite_id;

-- 2. Battery Degradation Trend
SELECT 
    packet_id,
    timestamp,
    battery_level,
    battery_voltage,
    battery_temp
FROM telemetry
ORDER BY packet_id DESC
LIMIT 100;

-- 3. Thermal Analysis
SELECT 
    AVG(thermal_main_bus) as avg_main_bus,
    AVG(thermal_payload) as avg_payload,
    AVG(thermal_battery) as avg_battery_temp,
    AVG(thermal_transmitter) as avg_transmitter,
    MAX(thermal_main_bus) as max_temp,
    MIN(thermal_main_bus) as min_temp
FROM telemetry
WHERE timestamp > datetime('now', '-1 hour');

-- 4. Communication Quality
SELECT 
    AVG(signal_strength) as avg_signal,
    AVG(data_rate_mbps) as avg_data_rate,
    AVG(link_margin_db) as avg_link_margin,
    CASE 
        WHEN signal_strength > 80 THEN 'Excellent'
        WHEN signal_strength > 60 THEN 'Good'
        WHEN signal_strength > 40 THEN 'Fair'
        ELSE 'Poor'
    END as quality_level,
    COUNT(*) as count
FROM telemetry
GROUP BY quality_level;

-- 5. Orbit Analysis
SELECT 
    MIN(altitude_km) as perigee,
    MAX(altitude_km) as apogee,
    AVG(velocity_kms) as avg_velocity,
    MIN(velocity_kms) as min_velocity,
    MAX(velocity_kms) as max_velocity
FROM telemetry;

-- 6. Anomaly Detection
SELECT 
    timestamp,
    packet_id,
    battery_level,
    thermal_main_bus,
    signal_strength,
    'CRITICAL' as severity
FROM telemetry
WHERE battery_level < 15 
   OR thermal_main_bus > 50 
   OR signal_strength < 40
UNION ALL
SELECT 
    timestamp,
    packet_id,
    battery_level,
    thermal_main_bus,
    signal_strength,
    'WARNING' as severity
FROM telemetry
WHERE (battery_level BETWEEN 15 AND 25)
   OR (thermal_main_bus BETWEEN 45 AND 50)
   OR (signal_strength BETWEEN 40 AND 55)
ORDER BY timestamp DESC
LIMIT 50;
