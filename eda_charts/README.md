# Output charts

These 15 PNG files are the saved outputs supplied with the project. Run the EDA notebook from the repository root to regenerate them.

## 1. Delivery time distribution

Histogram of delivery durations in minutes, showing the spread and most common delivery times.

![Delivery time distribution](01_delivery_time_distribution.png)

## 2. Delivery duration bands

Counts in the notebook duration bands: 20 minutes or less, 21-35, 36-60, and over 60 minutes.

![Delivery duration bands](02_delivery_bands.png)

## 3. Order categories

Number of recorded orders in each food category. This describes the dataset composition.

![Order categories](03_order_types.png)

## 4. Traffic and delivery duration

Mean delivery minutes for each traffic category. Jam records average 31.18 minutes, compared with 21.27 minutes for Low traffic.

![Traffic and delivery duration](04_traffic_delivery.png)

## 5. Weather and delivery duration

Boxplots compare median delivery duration and spread by weather condition; outlier points are hidden.

![Weather and delivery duration](05_weather_boxplot.png)

## 6. Vehicle performance

Mean delivery duration by vehicle type. Differences may also reflect route length, traffic, and vehicle assignment.

![Vehicle performance](06_vehicle_performance.png)

## 7. City type distribution

Number of delivery records by city classification, rather than by individual city or restaurant.

![City type distribution](07_city_types.png)

## 8. Daily recorded orders

Historical order counts by date. Missing dates are not automatically evidence of zero demand.

![Daily recorded orders](08_daily_volume.png)

## 9. Orders by hour

Recorded order counts by hour of day, excluding records whose order times could not be parsed.

![Orders by hour](09_hourly_orders.png)

## 10. Duration by order category

Mean delivery minutes for each order category, useful for comparing descriptive category averages.

![Duration by order category](10_food_delivery_time.png)

## 11. Weather and traffic together

Heatmap of mean delivery minutes for weather-traffic combinations. Group sizes can differ.

![Weather and traffic together](11_weather_traffic_heatmap.png)

## 12. Courier ratings and delivery time

Scatter plot of up to 4,000 complete records, sampled with random_state=42. Ratings refer to couriers.

![Courier ratings and delivery time](12_rating_vs_time.png)

## 13. Distance and delivery time

Scatter plot of up to 5,000 complete records, sampled with random_state=42. Haversine distance approximates straight-line distance.

![Distance and delivery time](13_distance_time.png)

## 14. Weekday comparison

Mean delivery duration from Monday through Sunday across the available historical records.

![Weekday comparison](14_weekday_comparison.png)

## 15. Numeric correlations

Pearson correlations between delivery duration and numeric features. Correlation does not establish causation.

![Numeric correlations](15_correlation_heatmap.png)
