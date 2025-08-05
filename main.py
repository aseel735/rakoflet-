import flet as ft
from datetime import datetime, date, timedelta

def main(page: ft.Page):
    page.title = "Multi-Berth Port Ship Service Planner"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    
    # Store ship data
    ships_data = []
    
    # Header
    title = ft.Text(
        "⚓ Multi-Berth Port Ship Service Planning System",
        size=28,
        weight=ft.FontWeight.BOLD,
        color="#1565C0"
    )
    
    subtitle = ft.Text(
        "Prepared by: Eng. Aseel Omar Ali Ahmed Qasem",
        size=16,
        italic=True,
        color="#616161"
    )
    
    description = ft.Text(
        "Configure your port settings and ships below, then click 'Calculate Schedule' to generate optimal berth assignments.",
        size=14,
        color="#757575"
    )
    
    # Port Configuration
    port_config_title = ft.Text(
        "🛠 Port Configuration",
        size=20,
        weight=ft.FontWeight.BOLD,
        color="#2E7D32"
    )
    
    num_berths_field = ft.TextField(
        label="Number of Berths",
        value="3",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER
    )
    
    # Ships Configuration
    ships_config_title = ft.Text(
        "🚢 Ship Details",
        size=20,
        weight=ft.FontWeight.BOLD,
        color="#1565C0"
    )
    
    num_ships_field = ft.TextField(
        label="Number of Ships",
        value="3",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER
    )
    
    # Container for ship input fields
    ships_container = ft.Column()
    
    # Results container
    results_container = ft.Column(visible=False)
    
    def update_ship_fields(e):
        """Update ship input fields based on number of ships"""
        try:
            num_ships = int(num_ships_field.value) if num_ships_field.value else 1
            num_ships = max(1, min(num_ships, 20))  # Limit between 1-20 ships
            
            ships_container.controls.clear()
            ships_data.clear()
            
            for i in range(num_ships):
                ship_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"Ship {i + 1}", size=16, weight=ft.FontWeight.BOLD),
                            ft.TextField(
                                label="Ship Name",
                                value=f"Ship-{i + 1}",
                                width=300,
                                data=f"name_{i}"
                            ),
                            ft.TextField(
                                label="Arrival Date (YYYY-MM-DD)",
                                value=date.today().strftime("%Y-%m-%d"),
                                width=300,
                                data=f"date_{i}",
                                helper_text="Format: YYYY-MM-DD"
                            ),
                            ft.TextField(
                                label="Arrival Time (HH:MM)",
                                value="08:00",
                                width=300,
                                data=f"time_{i}",
                                helper_text="Format: HH:MM (24-hour)"
                            ),
                            ft.TextField(
                                label="Number of Containers",
                                value="100",
                                width=300,
                                keyboard_type=ft.KeyboardType.NUMBER,
                                data=f"containers_{i}",
                                helper_text="Maximum: 5000 containers"
                            ),
                            ft.TextField(
                                label="Crane Capacity (containers/hour)",
                                value="30",
                                width=300,
                                keyboard_type=ft.KeyboardType.NUMBER,
                                data=f"crane_{i}",
                                helper_text="How many containers per hour"
                            )
                        ]),
                        padding=10
                    ),
                    margin=5
                )
                ships_container.controls.append(ship_card)
            
            page.update()
        except ValueError:
            pass
    
    def collect_ship_data():
        """Collect all ship data from input fields"""
        ships_data.clear()
        
        for ship_card in ships_container.controls:
            ship_fields = {}
            container_content = ship_card.content.content
            for control in container_content.controls:
                if isinstance(control, ft.TextField) and hasattr(control, 'data'):
                    field_type = control.data.split('_')[0]
                    ship_fields[field_type] = control.value
            
            if len(ship_fields) == 5:  # name, date, time, containers, crane
                try:
                    arrival_date = datetime.strptime(ship_fields['date'], "%Y-%m-%d").date()
                    arrival_time = datetime.strptime(ship_fields['time'], "%H:%M").time()
                    containers = min(int(ship_fields['containers']), 5000)  # Max 5000 containers
                    crane_capacity = int(ship_fields['crane'])
                    
                    # Calculate service duration based on containers and crane capacity
                    service_duration = max(1, containers / crane_capacity)  # Minimum 1 hour
                    
                    ships_data.append({
                        'name': ship_fields['name'],
                        'arrival_date': arrival_date,
                        'arrival_time': arrival_time,
                        'containers': containers,
                        'crane_capacity': crane_capacity,
                        'service_duration': service_duration
                    })
                except (ValueError, KeyError):
                    continue
    
    def calculate_schedule(e):
        """Calculate optimal berth schedule"""
        collect_ship_data()
        
        if not ships_data:
            show_error("Please enter valid ship data")
            return
        
        try:
            num_berths = int(num_berths_field.value) if num_berths_field.value else 1
            num_berths = max(1, num_berths)
            
            # Sort ships by arrival date and time
            ships_sorted = sorted(ships_data, key=lambda x: (x['arrival_date'], x['arrival_time']))
            
            # Simple berth allocation
            schedule = []
            berth_end_times = [datetime.combine(date.today(), datetime.min.time()) for _ in range(num_berths)]
            
            for ship in ships_sorted:
                ship_arrival = datetime.combine(ship['arrival_date'], ship['arrival_time'])
                assigned_berth = berth_end_times.index(min(berth_end_times))
                
                start_time = max(ship_arrival, berth_end_times[assigned_berth])
                end_time = start_time + timedelta(hours=ship['service_duration'])
                
                berth_end_times[assigned_berth] = end_time
                
                schedule.append({
                    'Ship': ship['name'],
                    'Berth': f'Berth {assigned_berth + 1}',
                    'Start': start_time.strftime('%Y-%m-%d %H:%M'),
                    'End': end_time.strftime('%Y-%m-%d %H:%M'),
                    'Containers': ship['containers'],
                    'Crane Capacity': f"{ship['crane_capacity']}/hr",
                    'Duration': f"{ship['service_duration']:.1f} hrs",
                    'start_datetime': start_time,
                    'end_datetime': end_time
                })
            
            display_results(schedule)
            
        except ValueError:
            show_error("Please enter valid numbers for berths and duration")
    
    def display_results(schedule):
        """Display schedule results"""
        results_container.controls.clear()
        
        # Results title
        results_title = ft.Text(
            "📋 Schedule Results",
            size=24,
            weight=ft.FontWeight.BOLD,
            color="#6A1B9A"
        )
        
        # Schedule table
        table_title = ft.Text(
            "🗓 Final Schedule Table",
            size=18,
            weight=ft.FontWeight.BOLD
        )
        
        # Create data table
        table_rows = []
        for item in schedule:
            table_rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item['Ship'])),
                    ft.DataCell(ft.Text(item['Berth'])),
                    ft.DataCell(ft.Text(item['Start'])),
                    ft.DataCell(ft.Text(item['End'])),
                    ft.DataCell(ft.Text(str(item['Containers']))),
                    ft.DataCell(ft.Text(item['Crane Capacity'])),
                    ft.DataCell(ft.Text(item['Duration']))
                ])
            )
        
        data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Ship")),
                ft.DataColumn(ft.Text("Berth")),
                ft.DataColumn(ft.Text("Start Time")),
                ft.DataColumn(ft.Text("End Time")),
                ft.DataColumn(ft.Text("Containers")),
                ft.DataColumn(ft.Text("Crane Cap.")),
                ft.DataColumn(ft.Text("Duration"))
            ],
            rows=table_rows,
            border=ft.border.all(2, "#E0E0E0"),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, "#E0E0E0"),
            horizontal_lines=ft.border.BorderSide(1, "#E0E0E0")
        )
        
        # Create simple timeline visualization
        timeline_title = ft.Text(
            "📊 Timeline Visualization",
            size=18,
            weight=ft.FontWeight.BOLD
        )
        
        # Create timeline bars
        timeline_container = ft.Column()
        
        # Get unique berths and create timeline for each
        berths = list(set([item['Berth'] for item in schedule]))
        berths.sort()
        
        for berth in berths:
            berth_ships = [item for item in schedule if item['Berth'] == berth]
            berth_title = ft.Text(berth, weight=ft.FontWeight.BOLD, color="#1565C0")
            
            berth_timeline = ft.Row()
            for ship in berth_ships:
                ship_bar = ft.Container(
                    content=ft.Text(
                        f"{ship['Ship']}\n{ship['Start']}-{ship['End']}\n{ship['Containers']} containers\n{ship['Duration']}", 
                        size=9,
                        text_align=ft.TextAlign.CENTER,
                        color="#FFFFFF"
                    ),
                    bgcolor="#42A5F5",
                    padding=5,
                    margin=2,
                    border_radius=5,
                    width=180
                )
                berth_timeline.controls.append(ship_bar)
            
            timeline_container.controls.extend([berth_title, berth_timeline, ft.Divider()])
        
        results_container.controls.extend([
            results_title,
            ft.Divider(),
            table_title,
            ft.Container(
                content=data_table,
                padding=10,
                bgcolor="#FFFFFF",
                border_radius=10,
                border=ft.border.all(1, "#E0E0E0")
            ),
            ft.Container(height=20),
            timeline_title,
            ft.Container(
                content=timeline_container,
                padding=10,
                bgcolor="#FFFFFF",
                border_radius=10,
                border=ft.border.all(1, "#E0E0E0")
            )
        ])
        
        results_container.visible = True
        page.update()
    
    def show_error(message):
        """Show error message"""
        error_dialog = ft.AlertDialog(
            title=ft.Text("خطأ"),
            content=ft.Text(message),
            actions=[ft.TextButton("موافق", on_click=lambda e: page.close(error_dialog))]
        )
        page.open(error_dialog)
    
    # Calculate button
    calculate_btn = ft.ElevatedButton(
        "Calculate Schedule",
        on_click=calculate_schedule,
        bgcolor="#1565C0",
        color="#FFFFFF",
        width=200,
        height=40
    )
    
    # Set up initial ship fields
    num_ships_field.on_change = update_ship_fields
    update_ship_fields(None)
    
    # Main layout
    page.add(
        ft.Column([
            title,
            subtitle,
            description,
            ft.Divider(),
            
            # Configuration section
            ft.Row([
                ft.Column([
                    port_config_title,
                    num_berths_field,
                    ft.Container(height=20),
                    ships_config_title,
                    num_ships_field
                ], width=300),
                
                ft.VerticalDivider(),
                
                ft.Column([
                    ships_container
                ], expand=True, scroll=ft.ScrollMode.AUTO)
            ], expand=True),
            
            ft.Container(height=20),
            calculate_btn,
            ft.Container(height=20),
            results_container
        ], scroll=ft.ScrollMode.AUTO)
    )

if __name__ == "__main__":
    ft.app(target=main, port=5000, view=ft.AppView.WEB_BROWSER)
