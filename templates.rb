module Nouns
	@@templates = {};

	def get_template(name)
		return @@templates[name];
	end

	def self.noun(name, &block)
		name = name.downcase
		@@templates[name] = block;
	end

	def spawn(which)
		if (which.class == Array) 
			return spawn_multiple(which); 
		end	

		which = which.downcase
		return if @@templates[which].nil?
		noun = Noun.new;
		noun.instance_eval &@@templates[which]
		return noun;
	end

	def spawn_multiple(*things)
		out = [];
		things.each do |thing|
			out << spawn(thing)
		end
		return out;
	end

	def has_guts
		container << spawn(:heart, :blood)
	end

	noun :stomach do
		name "a stomach"
		is :small, :digesting
	end

	noun :blood do
		name "some blood"
		is :blood
	end

	noun :mouse do
		name "a field mouse"
		is :small, :soft, :fuzzy
		contains :stomach, :heart, :brain, :blood
	end

	noun :mouse_stomach do
		like_a :stomach #but
		name "a mouse's stomach"
	end

	noun :bear do
		is :fuzzy, :container, :alive
		@name = "a bear"
		contains :stomach
	end

	noun :tea_kettle do
		is :hard, :medium, :container
		@name = "a tea kettle"
	end
end
