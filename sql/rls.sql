ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE games ENABLE ROW LEVEL SECURITY;
ALTER TABLE tournaments ENABLE ROW LEVEL SECURITY;
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE tournament_registrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE match_results ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_read_only" ON users FOR SELECT TO anon USING (true);
CREATE POLICY "games_read_only" ON games FOR SELECT TO anon USING (true);
CREATE POLICY "tournaments_read_only" ON tournaments FOR SELECT TO anon USING (true);
CREATE POLICY "teams_read_only" ON teams FOR SELECT TO anon USING (true);
CREATE POLICY "registrations_read_only" ON tournament_registrations FOR SELECT TO anon USING (true);
CREATE POLICY "matches_read_only" ON matches FOR SELECT TO anon USING (true);
CREATE POLICY "results_read_only" ON match_results FOR SELECT TO anon USING (true);
CREATE POLICY "users_can_register_as_user" ON public.users FOR INSERT TO anon WITH CHECK (role = 'user');