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
            
            # Define metrics to analyze
            metrics = {
                'Win Rate': {'func': lambda df: (df['battle_outcome'] == 'Victory').mean() * 100, 'cmap': 'YlGn'},
                'Casualty Rate': {'func': lambda df: (df['total_infantry_casualties_10'].sum() / df['total_infantry_used'].sum()) * 100 if df['total_infantry_used'].sum() > 0 else 0, 'cmap': 'YlOrRd'},
                'Troops Used': {'func': lambda df: df['total_infantry_used'].mean(), 'cmap': 'Blues'},
                'Pontoons Used': {'func': lambda df: df['total_pontoons_used'].mean(), 'cmap': 'Purples'},
                'Battle Duration': {'func': lambda df: df['ticks'].mean(), 'cmap': 'Oranges'}
            }
            
            # Create one figure per metric
            for metric_name, metric_info in metrics.items():
                fig = plt.figure(figsize=(16, 12))
                ax = fig.add_subplot(111, projection='3d')
                
                # Prepare data for scatter plot
                x_data, y_data, z_data, values = [], [], [], []
                
                # For each combination of parameters, calculate metric value
                for mode in site_modes:
                    for pause in wave_pauses:
                        for duration in wave_durations:
                            mask = ((self.data['site_selection_mode'] == mode) & 
                                    (self.data['wave-pause'] == pause) & 
                                    (self.data['wave-duration'] == duration))
                            
                            subset_data = self.data[mask]
                            
                            if len(subset_data) > 0:
                                x_data.append(pause)
                                y_data.append(duration)
                                z_data.append(mode_to_num[mode])
                                values.append(metric_info['func'](subset_data))
                
                # Normalize values for coloring
                if values:
                    norm = plt.Normalize(min(values), max(values))
                    colors = plt.cm.get_cmap(metric_info['cmap'])(norm(values))
                    
                    # Create scatter plot
                    scatter = ax.scatter(x_data, y_data, z_data, c=colors, 
                                        s=400, marker='o', alpha=0.8, edgecolor='black')
                    
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
                    ax.set_zticks(list(mode_to_num.values()))
                    ax.set_zticklabels(list(mode_to_num.keys()), rotation=30)
                    
                    # Adjust view angle
                    ax.view_init(elev=30, azim=45)
                    
                    plt.tight_layout()
                    
                    # Save figure
                    out_path = os.path.join(self.output_dir, f"3D_{metric_name.replace(' ', '_')}_Comparison.png")
                    plt.savefig(out_path, dpi=300, bbox_inches='tight')
                    print(f'3D {metric_name} comparison saved to "{out_path}".')
                    
                plt.close(fig)
            
        except Exception as e:
            print(f"An error occurred while creating 3D metrics comparisons: {e}")
    
    def _create_uniform_vs_waves_metrics_comparison(self):
        """Creates multiple bar charts comparing Waves (pause=70, duration=200) vs Uniform across various metrics."""
        try:
            # Set plot style
            self._set_plot_style()
            
            # Filter waves data for the specific parameters
            best_waves = self.data[(self.data['wave-pause']==70) & (self.data['wave-duration']==200)]
            
            # Load uniform data - try different methods to handle various data formats
            try:
                # First, check the first few lines to understand the format
                with open(self.uniform_file, 'r') as f:
                    first_lines = [next(f) for _ in range(10)]
                    print("First lines of Uniform data file:")
                    for i, line in enumerate(first_lines):
                        print(f"{i}: {line.strip()}")
                
                # skiprows=6 is common, but may need adjustment based on file format
                uni = pd.read_csv(self.uniform_file, skiprows=6)
                print("Available columns (Original Uniform data):", uni.columns.tolist())
                
                # Define all possible mappings from existing column names to standardized names
                column_mapping = {
                    # Standard names for site selection mode and battle outcome
                    'site-selection-mode': 'site_selection_mode',
                    'battle-outcome': 'battle_outcome',
                    
                    # Troops and pontoon data - various possible names
                    'total-infantry-used': 'total_infantry_used',
                    'infantry-used': 'total_infantry_used',
                    'infantry used': 'total_infantry_used',
                    
                    'total-infantry-casualties / 10': 'total_infantry_casualties_10',
                    'infantry-casualties': 'total_infantry_casualties_10',
                    'infantry casualties': 'total_infantry_casualties_10',
                    
                    'total-infantry-crossed': 'total_infantry_crossed',
                    'infantry-crossed': 'total_infantry_crossed',
                    'infantry crossed': 'total_infantry_crossed',
                    
                    'total-pontoons-used': 'total_pontoons_used',
                    'pontoons-used': 'total_pontoons_used',
                    'pontoons used': 'total_pontoons_used',
                    
                    # Time-related columns
                    '[step]': 'ticks',
                    'step': 'ticks',
                    'ticks': 'ticks'
                }
                
                # Compare column names case-insensitively
                lowercase_cols = {col.lower(): col for col in uni.columns}
                
                # Create a new mapping
                new_mapping = {}
                for original, target in column_mapping.items():
                    if original in uni.columns:  # Direct match
                        new_mapping[original] = target
                    elif original.lower() in lowercase_cols:  # Case-insensitive match
                        actual_col = lowercase_cols[original.lower()]
                        new_mapping[actual_col] = target
                
                if new_mapping:
                    uni = uni.rename(columns=new_mapping)
                    print("Column names after renaming (Uniform):", uni.columns.tolist())
                else:
                    print("Warning: No matching column mappings found. Keeping original column names.")
                    
                    # If no mappings found, try to guess based on column name content
                    cols = uni.columns.tolist()
                    # Guess site selection mode
                    site_mode_candidates = [c for c in cols if 'site' in c.lower() or 'mode' in c.lower() or 'select' in c.lower()]
                    if site_mode_candidates:
                        uni = uni.rename(columns={site_mode_candidates[0]: 'site_selection_mode'})
                    
                    # Guess battle outcome
                    outcome_candidates = [c for c in cols if 'outcome' in c.lower() or 'battle' in c.lower() or 'result' in c.lower()]
                    if outcome_candidates:
                        uni = uni.rename(columns={outcome_candidates[0]: 'battle_outcome'})
                    
                    print("Column names after guess-based renaming:", uni.columns.tolist())
            
            except Exception as e:
                print(f"Error loading uniform data: {e}")
                # Try loading the file in a different way
                try:
                    uni = pd.read_csv(self.uniform_file, skiprows=0)  # No header row
                    print("Columns with skiprows=0:", uni.columns.tolist())
                except Exception as e2:
                    print(f"Alternative loading also failed: {e2}")
                    return
            
            # Fix potential duplicate column names (ticks appears twice in some cases)
            if uni.columns.duplicated().any():
                print("Warning: Duplicate column names found in uniform data")
                # Create a new list of column names, making duplicates unique
                new_cols = []
                seen = set()
                for col in uni.columns:
                    if col in seen:
                        counter = 1
                        while f"{col}_{counter}" in seen:
                            counter += 1
                        new_cols.append(f"{col}_{counter}")
                    else:
                        new_cols.append(col)
                    seen.add(col if col not in seen else f"{col}_{counter}")
                uni.columns = new_cols
                print("Columns after fixing duplicates:", uni.columns.tolist())
            
            # Check for required columns
            if 'site_selection_mode' not in uni.columns or 'battle_outcome' not in uni.columns:
                print("Warning: Required columns not found in Uniform data. Available columns:", uni.columns.tolist())
                # Try provisional column assignment
                if len(uni.columns) >= 3 and 'site_selection_mode' not in uni.columns:
                    print(f"Provisionally using column {uni.columns[2]} as site_selection_mode")
                    uni = uni.rename(columns={uni.columns[2]: 'site_selection_mode'})
                
                if len(uni.columns) >= 4 and 'battle_outcome' not in uni.columns:
                    print(f"Provisionally using column {uni.columns[3]} as battle_outcome")
                    uni = uni.rename(columns={uni.columns[3]: 'battle_outcome'})
            
            # Define metrics to compare - start with just the basic Success Rate that's guaranteed
            metrics = [
                {
                    'name': 'Success Rate (%)',
                    'waves_func': lambda df: (df['battle_outcome'] == 'Victory').mean() * 100,
                    'uni_func': lambda df: (df['battle_outcome'] == 'Victory').mean() * 100,
                    'format': '{:.1f}%'
                }
            ]
            
            # Add additional metrics based on available columns
            for col_name, friendly_name, format_str in [
                ('total_infantry_casualties_10', 'Casualty Rate (%)', '{:.1f}%'),
                ('total_infantry_used', 'Troops Used', '{:.0f}'),
                ('total_pontoons_used', 'Pontoons Used', '{:.1f}'),
                ('ticks', 'Battle Duration (ticks)', '{:.0f}')
            ]:
                # Check if column exists in both datasets
                waves_has_col = col_name in best_waves.columns
                uni_has_col = col_name in uni.columns
                
                if waves_has_col and uni_has_col:
                    if col_name == 'total_infantry_casualties_10' and 'total_infantry_used' in best_waves.columns and 'total_infantry_used' in uni.columns:
                        # Special calculation for casualty rate
                        metrics.append({
                            'name': friendly_name,
                            'waves_func': lambda df: (df['total_infantry_casualties_10'].sum() / df['total_infantry_used'].sum()) * 100 if df['total_infantry_used'].sum() > 0 else 0,
                            'uni_func': lambda df: (df['total_infantry_casualties_10'].sum() / df['total_infantry_used'].sum()) * 100 if df['total_infantry_used'].sum() > 0 else 0,
                            'format': format_str
                        })
                    else:
                        # Normal mean calculation
                        metrics.append({
                            'name': friendly_name,
                            'waves_func': lambda df, col=col_name: df[col].mean(),
                            'uni_func': lambda df, col=col_name: df[col].mean(),
                            'format': format_str
                        })
            
            # Pontoon efficiency metric (only if required columns exist in both datasets)
            if all(col in best_waves.columns for col in ['total_infantry_crossed', 'total_pontoons_used']) and \
               all(col in uni.columns for col in ['total_infantry_crossed', 'total_pontoons_used']):
                metrics.append({
                    'name': 'Pontoon Efficiency (troops/pontoon)',
                    'waves_func': lambda df: (df['total_infantry_crossed'].mean() / df['total_pontoons_used'].mean()) if df['total_pontoons_used'].mean() > 0 else 0,
                    'uni_func': lambda df: (df['total_infantry_crossed'].mean() / df['total_pontoons_used'].mean()) if df['total_pontoons_used'].mean() > 0 else 0,
                    'format': '{:.1f}'
                })
            
            # Identify common modes
            all_modes = sorted(set(best_waves['site_selection_mode'].unique()).union(
                              set(uni['site_selection_mode'].unique())), key=str)
            
            # Create a chart for each metric
            for metric in metrics:
                fig, ax = plt.subplots(figsize=(14, 8))
                
                # Calculate values for each mode
                waves_values = []
                uni_values = []
                
                for mode in all_modes:
                    # Waves data
                    waves_mode_data = best_waves[best_waves['site_selection_mode'] == mode]
                    if len(waves_mode_data) > 0:
                        try:
                            value = metric['waves_func'](waves_mode_data)
                            # Ensure value is scalar
                            if hasattr(value, 'shape'):
                                print(f"Warning: Non-scalar value for waves mode {mode}, metric {metric['name']}: shape {value.shape}")
                                value = float(value) if value.size == 1 else value[0] if value.size > 0 else 0
                            waves_values.append(value)
                        except Exception as e:
                            print(f"Error calculating {metric['name']} for waves mode {mode}: {e}")
                            waves_values.append(0)
                    else:
                        waves_values.append(0)
                    
                    # Uniform data
                    uni_mode_data = uni[uni['site_selection_mode'] == mode]
                    if len(uni_mode_data) > 0:
                        try:
                            value = metric['uni_func'](uni_mode_data)
                            # Ensure value is scalar
                            if hasattr(value, 'shape'):
                                print(f"Warning: Non-scalar value for uniform mode {mode}, metric {metric['name']}: shape {value.shape}")
                                value = float(value) if value.size == 1 else value[0] if value.size > 0 else 0
                            uni_values.append(value)
                        except Exception as e:
                            print(f"Error calculating {metric['name']} for uniform mode {mode}: {e}")
                            uni_values.append(0)
                    else:
                        uni_values.append(0)
                
                # Verify arrays have the correct shape
                print(f"Diagnostic for {metric['name']}: waves_values shape {np.array(waves_values).shape}, uni_values shape {np.array(uni_values).shape}")
                
                # Ensure both arrays are 1D with same length
                waves_values = np.array(waves_values).flatten()
                uni_values = np.array(uni_values).flatten()
                
                if len(waves_values) != len(all_modes) or len(uni_values) != len(all_modes):
                    print(f"Error: Value arrays length mismatch for {metric['name']}: waves {len(waves_values)}, uni {len(uni_values)}, modes {len(all_modes)}")
                    waves_values = waves_values[:len(all_modes)] if len(waves_values) > len(all_modes) else np.pad(waves_values, (0, len(all_modes) - len(waves_values)))
                    uni_values = uni_values[:len(all_modes)] if len(uni_values) > len(all_modes) else np.pad(uni_values, (0, len(all_modes) - len(uni_values)))
                
                # Create bar chart
                x = np.arange(len(all_modes))
                width = 0.35
                
                try:
                    waves_bars = ax.bar(x - width/2, waves_values, width, label='Waves (p=70, d=200)', 
                                      color='#3498db', edgecolor='black', linewidth=0.8)
                    uni_bars = ax.bar(x + width/2, uni_values, width, label='Uniform', 
                                     color='#e74c3c', edgecolor='black', linewidth=0.8)
                except Exception as e:
                    print(f"Error creating bars for {metric['name']}: {e}")
                    print(f"waves_values: {waves_values}")
                    print(f"uni_values: {uni_values}")
                    continue  # Skip to next metric
                
                # Add value labels
                for bar, value in zip(waves_bars, waves_values):
                    height = bar.get_height()
                    if height > 0:  # Only show label if value is greater than zero
                        ax.annotate(metric['format'].format(value),
                                   xy=(bar.get_x() + bar.get_width()/2, height),
                                   xytext=(0, 3),  # 3 points vertical offset
                                   textcoords="offset points",
                                   ha='center', va='bottom', fontsize=9)
                
                for bar, value in zip(uni_bars, uni_values):
                    height = bar.get_height()
                    if height > 0:  # Only show label if value is greater than zero
                        ax.annotate(metric['format'].format(value),
                                   xy=(bar.get_x() + bar.get_width()/2, height),
                                   xytext=(0, 3),  # 3 points vertical offset
                                   textcoords="offset points",
                                   ha='center', va='bottom', fontsize=9)
                
                # Set chart properties
                ax.set_xlabel('Site Selection Strategy', fontsize=14, fontweight='bold')
                ax.set_ylabel(metric['name'], fontsize=14, fontweight='bold')
                ax.set_title(f'Waves vs Uniform: {metric["name"]} by Site Selection Mode', 
                            fontsize=16, fontweight='bold', pad=20)
                ax.set_xticks(x)
                ax.set_xticklabels(all_modes, rotation=45, ha='right')
                ax.legend(fontsize=12)
                
                # Add grid lines
                ax.grid(axis='y', linestyle='--', alpha=0.7)
                
                plt.tight_layout()
                
                # Generate safe filename
                safe_name = metric['name'].replace(' ', '_').replace('(', '').replace(')', '')
                safe_name = safe_name.replace('%', 'pct').replace('/', 'per')
                out_path = os.path.join(self.output_dir, f"Waves_vs_Uniform_{safe_name}.png")
                try:
                    plt.savefig(out_path, dpi=300, bbox_inches='tight')
                    print(f'Waves vs Uniform {metric["name"]} comparison saved to "{out_path}".')
                except Exception as e:
                    print(f"Failed to save {metric['name']} graph: {e}")
                    # Try backup filename
                    backup_path = os.path.join(self.output_dir, f"Waves_vs_Uniform_Metric_{metrics.index(metric)}.png")
                    try:
                        plt.savefig(backup_path, dpi=300, bbox_inches='tight')
                        print(f'Saved with backup filename: "{backup_path}"')
                    except Exception as e2:
                        print(f"Backup save also failed: {e2}")
                
                plt.close(fig)
            
        except Exception as e:
            import traceback
            print(f"An error occurred while creating Waves vs Uniform comparison: {e}")
            print(traceback.format_exc())  # Show detailed error trace

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
