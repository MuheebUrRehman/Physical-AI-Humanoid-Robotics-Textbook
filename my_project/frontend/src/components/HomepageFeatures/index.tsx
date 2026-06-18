import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

interface ModuleItem {
  number: string;
  icon: string;
  title: string;
  description: string;
  chapters: string[];
  href: string;
}

const modules: ModuleItem[] = [
  {
    number: '01',
    icon: '🧠',
    title: 'Foundations of Physical AI',
    description: 'Embodied intelligence, kinematics & dynamics, and the robotics stack that powers humanoid systems.',
    chapters: ['Chapter 1: Foundations of Physical AI', 'Chapter 2: ROS 2, The Robotic Nervous System'],
    href: '/docs/module1/chapter1',
  },
  {
    number: '02',
    icon: '🎮',
    title: 'Simulation Environments',
    description: 'Digital twins, physics simulation, and high-fidelity environments for robotic training and testing.',
    chapters: ['Chapter 3: Gazebo, Your First Digital Twin', 'Chapter 4: Unity, High-Fidelity Simulation'],
    href: '/docs/module2/chapter3',
  },
  {
    number: '03',
    icon: '🚀',
    title: 'Advanced Simulation & Perception',
    description: 'Isaac Sim, Isaac ROS, VSLAM, and navigation systems for real-world robotic perception.',
    chapters: ['Chapter 5: Isaac Sim, Isaac ROS, VSLAM, Navigation'],
    href: '/docs/module3/chapter5',
  },
  {
    number: '04',
    icon: '🔗',
    title: 'Integration & Capstone',
    description: 'Voice-to-action pipelines, LLM-based planning, and the final capstone integration project.',
    chapters: ['Chapter 6: Voice-to-Action, LLM Planning & Capstone'],
    href: '/docs/module4/chapter6',
  },
];

function ModuleCard({number, icon, title, description, chapters, href}: ModuleItem) {
  return (
    <Link to={href} className={styles.card}>
      <span className={styles.badge}>{number}</span>
      <div className={styles.icon}>{icon}</div>
      <h3 className={styles.cardTitle}>{title}</h3>
      <p className={styles.cardDesc}>{description}</p>
      <ul className={styles.chapterList}>
        {chapters.map((ch, i) => (
          <li key={i} className={styles.chapterItem}>{ch}</li>
        ))}
      </ul>
      <span className={styles.cta}>Explore Module →</span>
    </Link>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>Course Modules</h2>
      <p className={styles.subheading}>Explore the complete curriculum, from foundational concepts to the capstone integration project.</p>
      <div className={styles.grid}>
        {modules.map((mod) => (
          <ModuleCard key={mod.number} {...mod} />
        ))}
      </div>
    </section>
  );
}
