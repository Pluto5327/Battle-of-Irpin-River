import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # For 3D plotting
import matplotlib
matplotlib.use('Agg')


class IrpinDataAnalyzer:
    """Class for analyzing battle data of the Irpin River."""
    
    def __init__(self, script_dir=None):
        """Initialization method."""
        if script_dir is None:
            self.script_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            self.script_dir = script_dir
        
        self.output_dir = os.path.join(self.script_dir, "Waves - with Artillery")
        self.data_file = os.path.join(self.output_dir, "Waves_Data_Combined_Final.csv")  # Updated to use the provided file
        self.uniform_file = os.path.join(self.script_dir, 'Uniform - with Artillery', 'IrpinModel Vary Site-Selection Artillery Active-table.csv')
        self.data = None  # Variable to store the loaded data
        self.statistics = {}  # Dictionary to store computed statistics

    def load_data(self):
        """Loads the combined data from the provided CSV file."""
        print("Loading data from the combined CSV file.")
        try:
            # Load the data
            self.data = pd.read_csv(self.data_file)
            # Rename columns to use snake_case internal names
            self.data.rename(columns={
                'site-selection-mode': 'site_selection_mode',
                'battle-outcome': 'battle_outcome',
                'infantry-used': 'total_infantry_used',
                'infantry-casualties': 'total_infantry_casualties_10',
                'infantry-crossed': 'total_infantry_crossed',
                'pontoons-used': 'total_pontoons_used',
                '[step]': 'ticks'
            }, inplace=True)
            print("Columns after rename:", self.data.columns.tolist())
            print("Data successfully loaded.")
            print("----- Loaded Data (Head) -----")
            print(self.data.head())
        except Exception as e:
            print(f"An error occurred while loading the data: {e}")
            self.data = None
    
    def _standardize_column_names(self, T1, T2):
        """Internal method to standardize column names."""
        column_mapping = {
            'total-infantry-casualties / 10': 'total_infantry_casualties_10',
            'total-infantry-crossed': 'total_infantry_crossed',
            'total-infantry-used': 'total_infantry_used',
            'total-pontoons-used': 'total_pontoons_used',
            'site-selection-mode': 'site_selection_mode',
            'battle-outcome': 'battle_outcome'
        }
        T1 = T1.rename(columns=column_mapping)
        T2 = T2.rename(columns=column_mapping)
        return T1, T2
    
    def calculate_statistics(self):
        """Calculates statistical information of the data.
        
        Returns:
            dict: Dictionary containing the computed statistics.
        """
        if self.data is None:
            print("Data has not been loaded. Please run the load_data method first.")
            return None
        
        print("\nStarting statistical calculation.")
        
        # 1. Get unique site selection modes and battle outcomes
        site_modes = self.data['site_selection_mode'].unique()
        battle_outcomes = self.data['battle_outcome'].unique()
        
        self.statistics['site_modes'] = site_modes
        self.statistics['battle_outcomes'] = battle_outcomes
        
        # 2. Calculate win rate (percentage of 'Victory') for each site selection mode
        win_rate = {}
        for mode in site_modes:
            mode_idx = self.data['site_selection_mode'] == mode
            count_mode = mode_idx.sum()
            count_victory = (self.data.loc[mode_idx, 'battle_outcome'] == 'Victory').sum()
            win_rate[mode] = (count_victory / count_mode) * 100 if count_mode > 0 else 0
        
        self.statistics['win_rate'] = win_rate
        
        # 3. Calculate casualty rate for each site selection mode
        casualty_rate = {}
        for mode in site_modes:
            mode_idx = self.data['site_selection_mode'] == mode
            total_casualties = self.data.loc[mode_idx, 'total_infantry_casualties_10'].sum()
            total_used = self.data.loc[mode_idx, 'total_infantry_used'].sum()
            casualty_rate[mode] = (total_casualties / total_used) * 100 if total_used > 0 else 0
        
        self.statistics['casualty_rate'] = casualty_rate
        
        # 4. Calculate casualty rate per observation
        row_casualty_rate = (self.data['total_infantry_casualties_10'] / self.data['total_infantry_used']) * 100
        self.statistics['row_casualty_rate'] = row_casualty_rate
        
        # 5. Sort data by ticks (as time series) and calculate cumulative values
        sorted_data = self.data.sort_values(by='ticks').reset_index(drop=True)
        sorted_used = sorted_data['total_infantry_used']
        sorted_crossed = sorted_data['total_infantry_crossed']
        sorted_casualties = sorted_data['total_infantry_casualties_10']

        cum_used = sorted_used.cumsum()
        cum_crossed = sorted_crossed.cumsum()
        cum_casualties = sorted_casualties.cumsum()
        
        self.statistics['cum_used'] = cum_used
        self.statistics['cum_crossed'] = cum_crossed
        self.statistics['cum_casualties'] = cum_casualties
        
        # 6. Calculate mean and median for key indices for each site selection mode
        self._calculate_mode_statistics(site_modes)
        
        # 7. Calculate sum totals for each site selection mode
        self._calculate_mode_sums(site_modes)
        
        # Display example results
        print("\nWin rates for each site selection mode:")
        for mode in site_modes:
            print(f"{mode}: {win_rate[mode]:.2f}%")
            
        print("\nStatistical calculation completed.")
        return self.statistics
    
    def _calculate_mode_statistics(self, site_modes):
        """Internal method to calculate statistics grouped by site selection mode."""
        mean_used = {}
        median_used = {}
        mean_crossed = {}
        median_crossed = {}
        mean_casualties = {}
        median_casualties = {}
        
        for mode in site_modes:
            mode_idx = self.data['site_selection_mode'] == mode
            mean_used[mode] = self.data.loc[mode_idx, 'total_infantry_used'].mean()
            median_used[mode] = self.data.loc[mode_idx, 'total_infantry_used'].median()
            mean_crossed[mode] = self.data.loc[mode_idx, 'total_infantry_crossed'].mean()
            median_crossed[mode] = self.data.loc[mode_idx, 'total_infantry_crossed'].median()
            mean_casualties[mode] = self.data.loc[mode_idx, 'total_infantry_casualties_10'].mean()
            median_casualties[mode] = self.data.loc[mode_idx, 'total_infantry_casualties_10'].median()
        
        self.statistics['mean_used'] = mean_used
        self.statistics['median_used'] = median_used
        self.statistics['mean_crossed'] = mean_crossed
        self.statistics['median_crossed'] = median_crossed
        self.statistics['mean_casualties'] = mean_casualties
        self.statistics['median_casualties'] = median_casualties
    
    def _calculate_mode_sums(self, site_modes):
        """Internal method to calculate sum values grouped by site selection mode."""
        sum_used = {}
        sum_crossed = {}
        sum_casualties = {}
        
        for mode in site_modes:
            mode_idx = self.data['site_selection_mode'] == mode
            sum_used[mode] = self.data.loc[mode_idx, 'total_infantry_used'].sum()
            sum_crossed[mode] = self.data.loc[mode_idx, 'total_infantry_crossed'].sum()
            sum_casualties[mode] = self.data.loc[mode_idx, 'total_infantry_casualties_10'].sum()
        
        self.statistics['sum_used'] = sum_used
        self.statistics['sum_crossed'] = sum_crossed
        self.statistics['sum_casualties'] = sum_casualties
  

    def _create_3d_scatter_plot(self):
        """Internal method to create a 3D scatter plot with color-coded battle outcomes."""
        try:
            # Check if required columns exist for plotting
            required_columns = ['wave-pause', 'wave-duration', 'site_selection_mode', 'battle_outcome']
            for col in required_columns:
                if col not in self.data.columns:
                    print(f"Warning: Column '{col}' not found. Skipping 3D graph creation.")
                    return

            # Convert site selection (site_selection_mode) from category to numerical values
            categories = sorted(self.data['site_selection_mode'].unique())
            cat_to_num = {cat: idx for idx, cat in enumerate(categories)}
            numeric_site = self.data['site_selection_mode'].map(cat_to_num)
            
            # Create masks for battle outcomes for color coding
            victory_mask = self.data['battle_outcome'] == 'Victory'
            retreat_mask = self.data['battle_outcome'] == 'Retreat'

            # Set plot style
            self._set_plot_style()
            
            # Create 3D plot
            fig = plt.figure(figsize=(14, 12), dpi=100)
            ax = fig.add_subplot(111, projection='3d')
            
            # Plot the data points for Victory outcomes
            sc_victory = ax.scatter(
                self.data.loc[victory_mask, 'wave-pause'], 
                self.data.loc[victory_mask, 'wave-duration'], 
                numeric_site[victory_mask],
                c='#2ecc71', marker='o', label='Victory', s=90, alpha=0.85,
                edgecolor='white', linewidth=0.5
            )
            
            # Plot the data points for Retreat outcomes
            sc_retreat = ax.scatter(
                self.data.loc[retreat_mask, 'wave-pause'], 
                self.data.loc[retreat_mask, 'wave-duration'], 
                numeric_site[retreat_mask],
                c='#e74c3c', marker='X', label='Retreat', s=90, alpha=0.85,
                edgecolor='white', linewidth=0.5
            )

            # Adjust grid line style
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Set axes labels and title
            ax.set_xlabel("Wave Pause", fontsize=14, labelpad=15, fontweight='bold')
            ax.set_ylabel("Wave Duration", fontsize=14, labelpad=15, fontweight='bold')
            ax.set_zlabel("Site Selection Strategy", fontsize=14, labelpad=15, fontweight='bold')
            
            title = ax.set_title(
                "Battle Outcomes by Wave Parameters and Site Selection Strategy", 
                fontsize=16, pad=25, fontweight='bold', 
                color='#2c3e50'
            )
            
            # Convert Z-axis tick labels back to category names
            ax.set_zticks(list(cat_to_num.values()))
            ax.set_zticklabels([f"{cat}" for cat in cat_to_num.keys()], 
                            fontsize=10, rotation=15)
            
            # Adjust axes limits
            x_min, x_max = self.data['wave-pause'].min(), self.data['wave-pause'].max()
            y_min, y_max = self.data['wave-duration'].min(), self.data['wave-duration'].max()
            ax.set_xlim(x_min - (x_max-x_min)*0.1, x_max + (x_max-x_min)*0.1)
            ax.set_ylim(y_min - (y_max-y_min)*0.1, y_max + (y_max-y_min)*0.1)
            
            # Set legend
            legend = ax.legend(
                loc='upper right', 
                fontsize=13, 
                frameon=True,
                framealpha=0.9,
                edgecolor='#cccccc',
                title='Battle Outcome',
                title_fontsize=14
            )
            
            # Adjust view angle
            ax.view_init(elev=35, azim=30)
            
            plt.tight_layout()
            
            # Save the graph
            graph_output_file = os.path.join(self.output_dir, "3D_Scatter_Battle_Outcomes.png")
            plt.savefig(graph_output_file, dpi=300, bbox_inches='tight')
            print(f'3D graph saved to "{graph_output_file}".')

        except Exception as e:
            print(f"An error occurred while drawing the 3D graph: {e}")
            print(f"Error details: {str(e)}")
     
    def _set_plot_style(self):
        """Internal method to set the plotting style."""
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['axes.facecolor'] = 'white'
        
    def create_visualizations(self):
        """Generates visualizations for the data."""
        if self.data is None or not self.statistics:
            print("Data or statistical information missing. Please run load_data and calculate_statistics methods first.")
            return
            
        print("\nStarting visualization creation.")
        
        # Original visualizations
        self._create_3d_scatter_plot()
        self._create_win_rate_bar_chart()            
        self._create_casualty_rate_bar_chart()         
        self._create_combined_success_casualty_chart() 
        self._create_heatmap_wave_parameters()         
        self._create_3d_surface_plot()                 
        self._create_success_threshold_comparison()
        
        # New visualizations requested by the user
        print("\nCreating additional visualizations...")
        self._create_uniform_vs_waves_bymode_bar_chart()  # Add this one first to fix the error
        self._create_multiple_heatmaps()  # Create heatmaps for various metrics
        self._create_3d_metrics_comparisons()  # Create 3D plots for all metrics
        self._create_uniform_vs_waves_metrics_comparison()  # Create Waves vs Uniform comparisons
        
        print("All visualization creation completed.")

    def _create_win_rate_bar_chart(self):
        """Bar chart showing win rates for each site selection strategy."""
        try:
            # Set plot style
            self._set_plot_style()
            
            # Retrieve win rate data
            win_rate = self.statistics['win_rate']
            modes = list(win_rate.keys())
            rates = list(win_rate.values())
            
            # Set up the figure size
            plt.figure(figsize=(12, 8))
            
            # Create a colormap (gradient from yellow to green)
            colors = plt.cm.YlGn(np.array(rates) / 100)
            
            # Create bar chart
            bars = plt.bar(modes, rates, color=colors, width=0.6, edgecolor='black', linewidth=0.8)
            
            # Display win rate value on top of each bar
            for bar, rate in zip(bars, rates):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 2,
                        f'{rate:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            # Decorate the chart
            plt.title('Success Rate by Site Selection Strategy', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Site Selection Strategy', fontsize=14, fontweight='bold', labelpad=10)
            plt.ylabel('Success Rate (%)', fontsize=14, fontweight='bold', labelpad=10)
            plt.xticks(rotation=45, ha='right', fontsize=11)
            plt.ylim(0, 105)  # Display 0-100% with some margin
            
            # Grid lines
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            plt.tight_layout()
            
            # Save the graph
            graph_output_file = os.path.join(self.output_dir, "Success_Rate_by_Strategy.png")
            plt.savefig(graph_output_file, dpi=300, bbox_inches='tight')
            print(f'Success rate bar chart saved to "{graph_output_file}".')
            
        except Exception as e:
            print(f"An error occurred while drawing the win rate chart: {e}")
    
    def _create_casualty_rate_bar_chart(self):
        """Bar chart showing casualty rates for each site selection strategy."""
        try:
            # Set plot style
            self._set_plot_style()
            
            # Retrieve casualty rate data
            casualty_rate = self.statistics['casualty_rate']
            modes = list(casualty_rate.keys())
            rates = list(casualty_rate.values())
            
            # Set up the figure size
            plt.figure(figsize=(12, 8))
            
            # Create a colormap (gradient from yellow to red; higher casualty rate becomes redder)
            colors = plt.cm.YlOrRd(np.array(rates) / max(rates))
            
            # Create bar chart
            bars = plt.bar(modes, rates, color=colors, width=0.6, edgecolor='black', linewidth=0.8)
            
            # Display casualty rate on top of each bar
            for bar, rate in zip(bars, rates):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 2,
                        f'{rate:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            # Decorate the chart
            plt.title('Casualty Rate by Site Selection Strategy', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Site Selection Strategy', fontsize=14, fontweight='bold', labelpad=10)
            plt.ylabel('Casualty Rate (%)', fontsize=14, fontweight='bold', labelpad=10)
            plt.xticks(rotation=45, ha='right', fontsize=11)
            plt.ylim(0, max(rates) * 1.15)  # Provide a bit of extra room
            
            # Grid lines
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            plt.tight_layout()
            
            # Save the graph
            graph_output_file = os.path.join(self.output_dir, "Casualty_Rate_by_Strategy.png")
            plt.savefig(graph_output_file, dpi=300, bbox_inches='tight')
            print(f'Casualty rate bar chart saved to "{graph_output_file}".')
            
        except Exception as e:
            print(f"An error occurred while drawing the casualty rate chart: {e}")

    def _create_combined_success_casualty_chart(self):
        """Combined chart displaying both success and casualty rates for each site selection strategy."""
        try:
            # Set plot style
            self._set_plot_style()
            
            # Retrieve required data
            win_rate = self.statistics['win_rate']
            casualty_rate = self.statistics['casualty_rate']
            
            # Prepare the data
            modes = list(win_rate.keys())
            success_rates = list(win_rate.values())
            casualty_rates = [casualty_rate[mode] for mode in modes]
            
            # Set positions for the x-axis
            x = np.arange(len(modes))
            width = 0.35  # Bar width
            
            # Set up the figure
            fig, ax1 = plt.subplots(figsize=(14, 10))
            
            # Plot success rate bars (using the left y-axis)
            bars1 = ax1.bar(x - width/2, success_rates, width, color='#2ecc71', 
                        edgecolor='black', linewidth=0.8, label='Success Rate')
            ax1.set_ylabel('Success Rate (%)', fontsize=14, fontweight='bold', color='#2ecc71')
            ax1.tick_params(axis='y', labelcolor='#2ecc71')
            ax1.set_ylim(0, 105)  # Success rate range 0-100%
            
            # Create right y-axis for casualty rates
            ax2 = ax1.twinx()
            bars2 = ax2.bar(x + width/2, casualty_rates, width, color='#e74c3c', 
                        edgecolor='black', linewidth=0.8, label='Casualty Rate')
            ax2.set_ylabel('Casualty Rate (%)', fontsize=14, fontweight='bold', color='#e74c3c')
            ax2.tick_params(axis='y', labelcolor='#e74c3c')
            y_max = max(max(casualty_rates) * 1.15, 105)  # Provide some extra room
            ax2.set_ylim(0, y_max)
            
            # Set site selection strategy on the x-axis
            ax1.set_xticks(x)
            ax1.set_xticklabels(modes, rotation=45, ha='right', fontsize=11)
            ax1.set_xlabel('Site Selection Strategy', fontsize=14, fontweight='bold', labelpad=10)
            
            # Display value labels
            for i, bar in enumerate(bars1):
                height = bar.get_height()
                ax1.annotate(f'{success_rates[i]:.1f}%', 
                            xy=(bar.get_x() + bar.get_width()/2, height),
                            xytext=(0, 3),  # 3 points above
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            for i, bar in enumerate(bars2):
                height = bar.get_height()
                ax2.annotate(f'{casualty_rates[i]:.1f}%', 
                            xy=(bar.get_x() + bar.get_width()/2, height),
                            xytext=(0, 3),  # 3 points above
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            # Set chart title and legend
            ax1.set_title('Comparison of Success and Casualty Rates by Site Selection Strategy', 
                        fontsize=16, fontweight='bold', pad=20)
            
            # Combine legends from both axes
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=12)
            
            # Grid lines (only on the left y-axis)
            ax1.grid(True, linestyle='--', alpha=0.7, axis='y')
            
            plt.tight_layout()
            
            # Save the graph
            graph_output_file = os.path.join(self.output_dir, "Success_vs_Casualty_Combined.png")
            plt.savefig(graph_output_file, dpi=300, bbox_inches='tight')
            print(f'Combined chart saved to "{graph_output_file}".')
            
        except Exception as e:
            print(f"An error occurred while drawing the combined chart: {e}")

    def _create_heatmap_wave_parameters(self):
        """Heatmap for win rate and casualty rate based on wave-pause and wave-duration."""
        try:
            # Set plot style
            self._set_plot_style()
            
            # Divide wave parameters into bins
            wave_pause_bins = sorted(self.data['wave-pause'].unique())
            wave_duration_bins = sorted(self.data['wave-duration'].unique())
            
            # Initialize matrices to store heatmap data for win rate and casualty rate
            win_rate_matrix = np.zeros((len(wave_pause_bins), len(wave_duration_bins)))
            casualty_rate_matrix = np.zeros((len(wave_pause_bins), len(wave_duration_bins)))
            
            # Calculate win rate and casualty rate for each combination of bins
            for i, pause in enumerate(wave_pause_bins):
                for j, duration in enumerate(wave_duration_bins):
                    # Extract data corresponding to the current bin
                    mask = (self.data['wave-pause'] == pause) & (self.data['wave-duration'] == duration)
                    bin_data = self.data[mask]
                    
                    if len(bin_data) > 0:
                        # Calculate win rate (percentage of Victory)
                        victory_count = (bin_data['battle_outcome'] == 'Victory').sum()
                        win_rate_matrix[i, j] = (victory_count / len(bin_data)) * 100
                        
                        # Calculate casualty rate
                        casualties = bin_data['total_infantry_casualties_10'].sum()
                        used = bin_data['total_infantry_used'].sum()
                        if used > 0:
                            casualty_rate_matrix[i, j] = (casualties / used) * 100
                        else:
                            casualty_rate_matrix[i, j] = 0
            
            # Display the two heatmaps side by side
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
            
            # Heatmap for win rate
            im1 = ax1.imshow(win_rate_matrix, cmap='YlGn', interpolation='nearest', aspect='auto')
            ax1.set_title('Success Rate (%)', fontsize=16, fontweight='bold')
            ax1.set_xlabel('Wave Duration', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Wave Pause', fontsize=14, fontweight='bold')
            ax1.set_xticks(range(len(wave_duration_bins)))
            ax1.set_yticks(range(len(wave_pause_bins)))
            ax1.set_xticklabels(wave_duration_bins)
            ax1.set_yticklabels(wave_pause_bins)
            
            # Add colorbar for win rate heatmap
            cbar1 = fig.colorbar(im1, ax=ax1)
            cbar1.set_label('Success Rate (%)', fontsize=12, fontweight='bold')
            
            # Heatmap for casualty rate
            im2 = ax2.imshow(casualty_rate_matrix, cmap='YlOrRd', interpolation='nearest', aspect='auto')
            ax2.set_title('Casualty Rate (%)', fontsize=16, fontweight='bold')
            ax2.set_xlabel('Wave Duration', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Wave Pause', fontsize=14, fontweight='bold')
            ax2.set_xticks(range(len(wave_duration_bins)))
            ax2.set_yticks(range(len(wave_pause_bins)))
            ax2.set_xticklabels(wave_duration_bins)
            ax2.set_yticklabels(wave_pause_bins)
            
            # Add colorbar for casualty rate heatmap
            cbar2 = fig.colorbar(im2, ax=ax2)
            cbar2.set_label('Casualty Rate (%)', fontsize=12, fontweight='bold')
            
            # Display cell values
            for i in range(len(wave_pause_bins)):
                for j in range(len(wave_duration_bins)):
                    ax1.text(j, i, f'{win_rate_matrix[i, j]:.1f}%', 
                             ha='center', va='center', color='black', fontsize=10)
                    ax2.text(j, i, f'{casualty_rate_matrix[i, j]:.1f}%', 
                             ha='center', va='center', color='black', fontsize=10)
            
            plt.tight_layout()
            
            # Save the graph
            graph_output_file = os.path.join(self.output_dir, "Wave_Parameters_Heatmap.png")
            plt.savefig(graph_output_file, dpi=300, bbox_inches='tight')
            print(f'Heatmap saved to "{graph_output_file}".')
            
        except Exception as e:
            print(f"An error occurred while drawing the heatmap: {e}")

    def _create_3d_surface_plot(self):
        """3D surface plot for win rate as a function of wave-pause and wave-duration."""
        try:
            # Set plot style
            self._set_plot_style()
            
            # Divide wave parameters into bins
            wave_pause_bins = sorted(self.data['wave-pause'].unique())
            wave_duration_bins = sorted(self.data['wave-duration'].unique())
            
            # Prepare grid data for 3D surface plot
            X, Y = np.meshgrid(wave_pause_bins, wave_duration_bins)
            Z = np.zeros((len(wave_duration_bins), len(wave_pause_bins)))
            
            # Calculate win rate data
            for i, duration in enumerate(wave_duration_bins):
                for j, pause in enumerate(wave_pause_bins):
                    mask = (self.data['wave-pause'] == pause) & (self.data['wave-duration'] == duration)
                    data_bin = self.data[mask]
                    if len(data_bin) > 0:
                        win_count = (data_bin['battle_outcome'] == 'Victory').sum()
                        Z[i, j] = (win_count / len(data_bin)) * 100
            
            # Create the plot
            fig = plt.figure(figsize=(14, 12))
            ax = fig.add_subplot(111, projection='3d')
            
            # 3D surface plot
            surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.8,
                                  linewidth=0, antialiased=True)
            
            # Decorate the plot
            ax.set_title('Success Rate as a Function of Wave Parameters', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Wave Pause', fontsize=14, fontweight='bold', labelpad=15)
            ax.set_ylabel('Wave Duration', fontsize=14, fontweight='bold', labelpad=15)
            ax.set_zlabel('Success Rate (%)', fontsize=14, fontweight='bold', labelpad=15)
            
            # Add a colorbar
            cbar = fig.colorbar(surf, ax=ax, shrink=0.7, aspect=10)
            cbar.set_label('Success Rate (%)', fontsize=12, fontweight='bold')
            
            # Adjust viewing angle
            ax.view_init(elev=30, azim=45)
            
            plt.tight_layout()
            
            # Save the graph
            graph_output_file = os.path.join(self.output_dir, "Success_Rate_Surface_3D.png")
            plt.savefig(graph_output_file, dpi=300, bbox_inches='tight')
            print(f'3D surface plot saved to "{graph_output_file}".')
            
        except Exception as e:
            print(f"An error occurred while drawing the 3D surface plot: {e}")

    def _create_success_threshold_comparison(self):
        """Creates heatmaps showing success rate extremes by strategy performance categories."""
        try:
            self._set_plot_style()
            # Determine high and low performance strategies
            win_rates = self.statistics['win_rate']
            sorted_modes = sorted(win_rates.items(), key=lambda x: x[1])
            half = len(sorted_modes) // 2
            low = [m for m, _ in sorted_modes[:half]]
            high = [m for m, _ in sorted_modes[-half:]]
            pauses = sorted(self.data['wave-pause'].unique())
            durations = sorted(self.data['wave-duration'].unique())
            high_mat = np.zeros((len(pauses), len(durations)))
            low_mat = np.zeros_like(high_mat)
            for i, p in enumerate(pauses):
                for j, d in enumerate(durations):
                    df_h = self.data[(self.data['wave-pause'] == p) & (self.data['wave-duration'] == d) & self.data['site_selection_mode'].isin(high)]
                    df_l = self.data[(self.data['wave-pause'] == p) & (self.data['wave-duration'] == d) & self.data['site_selection_mode'].isin(low)]
                    if len(df_h):
                        high_mat[i, j] = (df_h['battle_outcome'] == 'Victory').mean() * 100
                    if len(df_l):
                        low_mat[i, j] = (df_l['battle_outcome'] == 'Victory').mean() * 100
            # Plot heatmaps side by side
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
            im1 = ax1.imshow(high_mat, cmap='YlGn', vmin=0, vmax=100, aspect='auto')
            ax1.set_title('High-Performance Strategies')
            ax1.set_xticks(range(len(durations)))
            ax1.set_xticklabels(durations)
            ax1.set_yticks(range(len(pauses)))
            ax1.set_yticklabels(pauses)
            fig.colorbar(im1, ax=ax1, label='Success Rate (%)')
            im2 = ax2.imshow(low_mat, cmap='YlOrRd', vmin=0, vmax=100, aspect='auto')
            ax2.set_title('Low-Performance Strategies')
            ax2.set_xticks(range(len(durations)))
            ax2.set_xticklabels(durations)
            ax2.set_yticks(range(len(pauses)))
            ax2.set_yticklabels(pauses)
            fig.colorbar(im2, ax=ax2, label='Success Rate (%)')
            plt.suptitle('Success by Strategy Performance')
            plt.tight_layout()
            out = os.path.join(self.output_dir, 'Success_Strategy_Comparison.png')
            plt.savefig(out, dpi=300)
            print(f'Saved strategy comparison heatmap to {out}')
        except Exception as e:
            print(f"Error drawing strategy comparison: {e}")

    def _create_uniform_vs_waves_bymode_bar_chart(self):
        """Bar chart comparing success rates by site selection mode between Waves (pause=70,duration=200) and Uniform."""
        try:
            self._set_plot_style()
            # Waves best subset grouped by mode
            best = self.data[(self.data['wave-pause']==70)&(self.data['wave-duration']==200)]
            waves_success = best.groupby('site_selection_mode')['battle_outcome']\
                                 .apply(lambda x: (x=='Victory').mean()*100)
            # Load and standardize uniform data (skiprows=6 for correct parsing)
            uni = pd.read_csv(self.uniform_file, skiprows=6)
            uni.rename(columns={
                'site-selection-mode':'site_selection_mode',
                'battle-outcome':'battle_outcome'
            }, inplace=True)
            uniform_success = uni.groupby('site_selection_mode')['battle_outcome']\
                                  .apply(lambda x: (x=='Victory').mean()*100)
            # Combine all unique modes and sort as strings (not float)
            modes = sorted(set(waves_success.index).union(uniform_success.index), key=str)
            x = np.arange(len(modes))
            width = 0.35
            fig, ax = plt.subplots(figsize=(12,6))
            ax.bar(x-width/2, [waves_success.get(m,0) for m in modes], width, label='Waves')
            ax.bar(x+width/2, [uniform_success.get(m,0) for m in modes], width, label='Uniform')
            ax.set_xticks(x)
            ax.set_xticklabels(modes, rotation=45)
            ax.set_ylabel('Success Rate (%)')
            ax.set_title('Waves vs Uniform Success Rate by Site Selection Mode (pause=70,duration=200)')
            ax.legend()
            plt.tight_layout()
            out = os.path.join(self.output_dir, 'Waves_vs_Uniform_by_Mode.png')
            plt.savefig(out, dpi=300)
            print(f'Saved by-mode comparison chart to {out}')
        except Exception as e:
            print(f'Error drawing by-mode comparison: {e}')
    
    def _create_multiple_heatmaps(self):
        """Creates multiple heatmaps comparing different metrics based on wave parameters."""
        try:
            # Set plot style
            self._set_plot_style()
            
            # Get wave parameters
            wave_pause_bins = sorted(self.data['wave-pause'].unique())
            wave_duration_bins = sorted(self.data['wave-duration'].unique())
            
            # Define metrics to analyze
            metrics = {
                'Win Rate': lambda df: (df['battle_outcome'] == 'Victory').mean() * 100,
                'Casualty Rate': lambda df: (df['total_infantry_casualties_10'].sum() / df['total_infantry_used'].sum()) * 100 if df['total_infantry_used'].sum() > 0 else 0,
                'Troops Used': lambda df: df['total_infantry_used'].mean(),
                'Pontoons Used': lambda df: df['total_pontoons_used'].mean(),
                'Ticks (Duration)': lambda df: df['ticks'].mean()
            }
            
            # Use a 3x2 subplot grid for all metrics
            fig, axes = plt.subplots(3, 2, figsize=(20, 24))
            axes = axes.flatten()  # Flatten for easier indexing
            
            # Set colormaps for different metrics
            colormaps = {
                'Win Rate': 'YlGn',
                'Casualty Rate': 'YlOrRd',
                'Troops Used': 'Blues',
                'Pontoons Used': 'Purples',
                'Ticks (Duration)': 'Oranges'
            }
            
            # Create heatmap for each metric
            for i, (metric_name, metric_func) in enumerate(metrics.items()):
                if i >= len(axes):
                    break  # Safety check in case we have more metrics than axes
                
                # Create data matrix for this metric
                data_matrix = np.zeros((len(wave_pause_bins), len(wave_duration_bins)))
                
                # Calculate metric value for each wave parameter combination
                for p_idx, pause in enumerate(wave_pause_bins):
                    for d_idx, duration in enumerate(wave_duration_bins):
                        mask = (self.data['wave-pause'] == pause) & (self.data['wave-duration'] == duration)
                        data_bin = self.data[mask]
                        if len(data_bin) > 0:
                            data_matrix[p_idx, d_idx] = metric_func(data_bin)
                
                # Draw heatmap
                ax = axes[i]
                im = ax.imshow(data_matrix, cmap=colormaps.get(metric_name, 'viridis'), 
                              interpolation='nearest', aspect='auto')
                
                # Add colorbar
                cbar = fig.colorbar(im, ax=ax)
                cbar.set_label(metric_name, fontsize=12, fontweight='bold')
                
                # Label axes
                ax.set_title(f'{metric_name} by Wave Parameters', fontsize=16, fontweight='bold')
                ax.set_xlabel('Wave Duration', fontsize=14, fontweight='bold')
                ax.set_ylabel('Wave Pause', fontsize=14, fontweight='bold')
                ax.set_xticks(range(len(wave_duration_bins)))
                ax.set_yticks(range(len(wave_pause_bins)))
                ax.set_xticklabels(wave_duration_bins)
                ax.set_yticklabels(wave_pause_bins)
                
                # Add text labels to cells
                for p_idx in range(len(wave_pause_bins)):
                    for d_idx in range(len(wave_duration_bins)):
                        # Format differs based on metric
                        if 'Rate' in metric_name:
                            text = f'{data_matrix[p_idx, d_idx]:.1f}%'
                        elif 'Troops' in metric_name or 'Pontoons' in metric_name:
                            text = f'{data_matrix[p_idx, d_idx]:.1f}'
                        else:
                            text = f'{data_matrix[p_idx, d_idx]:.0f}'
                        
                        # Add text with contrasting color depending on background
                        text_color = 'white' if im.norm(data_matrix[p_idx, d_idx]) > 0.5 else 'black'
                        ax.text(d_idx, p_idx, text, ha='center', va='center', 
                               color=text_color, fontsize=9, fontweight='bold')
            
            # Remove unused subplot if any
            if len(metrics) < len(axes):
                for j in range(len(metrics), len(axes)):
                    fig.delaxes(axes[j])
            
            plt.tight_layout()
            
            # Save the graph
            graph_output_file = os.path.join(self.output_dir, "Multiple_Metrics_Heatmaps.png")
            plt.savefig(graph_output_file, dpi=300, bbox_inches='tight')
            print(f'Multiple metrics heatmaps saved to "{graph_output_file}".')
            
        except Exception as e:
            print(f"An error occurred while drawing multiple heatmaps: {e}")
    
    def _create_3d_metrics_comparisons(self):
        """Creates 3D plots comparing Wave Pause, Wave Duration, and Site Selection with various metrics."""
        try:
            # Set plot style
            self._set_plot_style()
            
            # Get parameters
            site_modes = sorted(self.data['site_selection_mode'].unique())
            wave_pauses = sorted(self.data['wave-pause'].unique())
            wave_durations = sorted(self.data['wave-duration'].unique())
            
            # Create numerical mapping for site selection modes
            mode_to_num = {mode: i for i, mode in enumerate(site_modes)}
            
            # Define metrics to analyze with functions and color maps
            metrics = {
                'Win Rate': {'func': lambda df: (df['battle_outcome'] == 'Victory').mean() * 100, 'cmap': 'YlGn'},
                'Casualty Rate': {'func': lambda df: (df['total_infantry_casualties_10'].sum() / df['total_infantry_used'].sum()) * 100 
                                  if df['total_infantry_used'].sum() > 0 else 0, 'cmap': 'YlOrRd'},
                'Troops Used': {'func': lambda df: df['total_infantry_used'].mean(), 'cmap': 'Blues'},
                'Pontoons Used': {'func': lambda df: df['total_pontoons_used'].mean(), 'cmap': 'Purples'},
                'Battle Duration': {'func': lambda df: df['ticks'].mean(), 'cmap': 'Oranges'}
            }
            
            # Calculate all data points once to avoid redundant calculations
            grid_data = self._calculate_3d_grid_data(site_modes, wave_pauses, wave_durations, metrics)
            
            # Create a separate plot for each metric
            for metric_name, metric_info in metrics.items():
                self._create_single_3d_metric_plot(metric_name, metric_info, grid_data, mode_to_num)
                
        except Exception as e:
            print(f"An error occurred while creating 3D metrics comparisons: {e}")
            import traceback
            print(traceback.format_exc())
    
    def _calculate_3d_grid_data(self, site_modes, wave_pauses, wave_durations, metrics):
        """Calculates all data points for 3D visualizations.
        
        Args:
            site_modes: List of site selection modes
            wave_pauses: List of wave pause values
            wave_durations: List of wave duration values
            metrics: Dictionary of metrics with their calculation functions
            
        Returns:
            Dictionary containing calculated values for each parameter combination
        """
        # Initialize results dictionary
        grid_data = {}
        
        # Group data by the three parameters to avoid redundant filtering
        grouped = self.data.groupby(['site_selection_mode', 'wave-pause', 'wave-duration'])
        
        # For each parameter combination, calculate all metrics
        for (mode, pause, duration), group in grouped:
            if len(group) > 0:  # Ensure we have data for this combination
                key = (mode, pause, duration)
                grid_data[key] = {
                    'x': pause,                    # Wave pause (x-axis)
                    'y': duration,                 # Wave duration (y-axis)
                    'z': mode,                     # Site selection mode (z-axis)
                    'values': {}                   # Will hold values for each metric
                }
                
                # Calculate each metric for this parameter combination
                for metric_name, metric_info in metrics.items():
                    try:
                        grid_data[key]['values'][metric_name] = metric_info['func'](group)
                    except Exception as e:
                        print(f"Error calculating {metric_name} for {key}: {e}")
                        grid_data[key]['values'][metric_name] = 0
        
        return grid_data
    
    def _create_single_3d_metric_plot(self, metric_name, metric_info, grid_data, mode_to_num):
        """Creates a single 3D plot for a specific metric.
        
        Args:
            metric_name: Name of the metric to visualize
            metric_info: Dictionary with function and colormap for the metric
            grid_data: Pre-calculated data points
            mode_to_num: Dictionary mapping site selection modes to numerical indices
        """
        # Extract data for this specific metric
        x_data, y_data, z_data, values = [], [], [], []
        
        for key, data in grid_data.items():
            if metric_name in data['values']:
                x_data.append(data['x'])
                y_data.append(data['y'])
                z_data.append(mode_to_num[data['z']])
                values.append(data['values'][metric_name])
        
        # Create plot if we have data
        if not values:
            print(f"No data available for metric: {metric_name}")
            return
            
        # Create figure and 3D axes
        fig = plt.figure(figsize=(16, 12))
        ax = fig.add_subplot(111, projection='3d')
        
        # Normalize values for coloring
        norm = plt.Normalize(min(values), max(values))
        colors = plt.cm.get_cmap(metric_info['cmap'])(norm(values))
        
        # Create scatter plot with size proportional to value importance
        sizes = np.array(values)
        sizes = 200 + 300 * (sizes - min(sizes)) / (max(sizes) - min(sizes)) if max(sizes) > min(sizes) else 400
        
        scatter = ax.scatter(x_data, y_data, z_data, c=colors, 
                            s=sizes, marker='o', alpha=0.8, edgecolor='black', linewidth=0.5)
        
        # Add colorbar
        cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=metric_info['cmap']), 
                           ax=ax, pad=0.1, shrink=0.7)
        cbar.set_label(metric_name, fontsize=14, fontweight='bold')
        
        # Set labels and title
        ax.set_xlabel('Wave Pause', fontsize=14, fontweight='bold', labelpad=10)
        ax.set_ylabel('Wave Duration', fontsize=14, fontweight='bold', labelpad=10)
        ax.set_zlabel('Site Selection Strategy', fontsize=14, fontweight='bold', labelpad=10)
        ax.set_title(f'3D Comparison of {metric_name}', fontsize=16, fontweight='bold', pad=20)
        
        # Set z-axis ticks to use site selection mode names
        modes = list(mode_to_num.keys())
        ax.set_zticks(range(len(modes)))
        ax.set_zticklabels(modes, rotation=30)
        
        # Add grid and adjust view angle
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.view_init(elev=30, azim=45)
        
        plt.tight_layout()
        
        # Save figure with a descriptive filename
        safe_metric_name = metric_name.replace(' ', '_')
        out_path = os.path.join(self.output_dir, f"3D_{safe_metric_name}_Comparison.png")
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        print(f'3D {metric_name} comparison saved to "{out_path}".')
        
        plt.close(fig)

def main():
    """Main function."""
    print("Starting script.")
    
    # Instantiate the analysis class
    analyzer = IrpinDataAnalyzer()
    
    # Step 1: Load the combined data
    analyzer.load_data()
    
    # Step 2: Calculate statistical information
    if analyzer.data is not None:
        analyzer.calculate_statistics()
        
        # Step 3: Generate visualizations
        analyzer.create_visualizations()
    
    print("Script finished.")


if __name__ == '__main__':
    main()
